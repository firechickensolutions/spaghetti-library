import { createElement } from '@lwc/engine-dom';
import RelatedActivityBoard from 'c/relatedActivityBoard';
import { graphql } from 'lightning/graphql';

jest.mock('lightning/graphql', () => {
    const { createTestWireAdapter } = jest.requireActual('@salesforce/sfdx-lwc-jest');
    return { gql: (parts) => parts[0], graphql: createTestWireAdapter() };
});

const visibleCase = {
    Id: '500000000000001AAA',
    ApiName: 'Case',
    DisplayValue: 'Practice case'
};

const differentCase = {
    Id: '500000000000002AAA',
    ApiName: 'Case',
    DisplayValue: 'Second practice case'
};

const practiceCaseDetails = {
    Id: visibleCase.Id,
    CaseNumber: { value: 'TRAIN-001' },
    Status: { value: 'New' },
    Priority: { value: 'High' }
};

function task(id, subject, status, parent) {
    return {
        Id: id,
        Subject: { value: subject },
        Status: { value: status },
        What: parent
    };
}

const firstTask = task('00T000000000001EAA', 'Check delivery', 'Not Started', visibleCase);
const secondTask = task('00T000000000002EAA', 'Confirm details', 'In Progress');
const matchesTasks = ({ query }) => query?.includes('query RelatedActivityTasks');
const matchesCases = ({ query }) => query?.includes('query RelatedActivityCaseDetails');

function emitTasks(nodes, hasNextPage = false, refresh) {
    const Task = { edges: nodes.map((node) => ({ node })), pageInfo: { hasNextPage } };
    graphql.emit({ data: { uiapi: { query: { Task } } }, refresh }, matchesTasks);
}

function emitCases(nodes, refresh) {
    const Case = { edges: nodes.map((node) => ({ node })) };
    graphql.emit({ data: { uiapi: { query: { Case } } }, refresh }, matchesCases);
}

async function renderBoard() {
    const element = createElement('c-related-activity-board', { is: RelatedActivityBoard });
    element.showCaseNumber = true;
    element.showCaseStatus = true;
    document.body.appendChild(element);
    await Promise.resolve();
    return element;
}

function caseRows(element) {
    return Array.from(element.shadowRoot.querySelectorAll('.case-row dd'), (row) => row.textContent);
}

afterEach(() => {
    document.body.replaceChildren();
});

it('groups task cards and displays only the Case fields selected in App Builder', async () => {
    const element = await renderBoard();
    expect(element.shadowRoot.textContent).toContain('Loading tasks');
    element.showCaseStatus = false;
    element.showCasePriority = true;

    emitTasks([firstTask, secondTask]);
    await Promise.resolve();
    expect(graphql.getLastConfig().variables).toEqual({ caseIds: [visibleCase.Id] });
    emitCases([practiceCaseDetails]);
    await Promise.resolve();

    const columns = [...element.shadowRoot.querySelectorAll('h2')];
    expect(columns.map((column) => column.textContent)).toEqual(['Not Started (1)', 'In Progress (1)']);
    expect(element.shadowRoot.querySelector('.related-link').label).toBe('Practice case');
    expect(caseRows(element)).toEqual(['TRAIN-001', 'High']);
});

it('keeps the task and permitted fields when the Case response omits a field', async () => {
    const element = await renderBoard();
    emitTasks([firstTask, secondTask]);
    await Promise.resolve();
    emitCases([{ Id: visibleCase.Id, Status: { value: 'New' } }]);
    await Promise.resolve();

    expect(element.shadowRoot.querySelectorAll('.task-card')).toHaveLength(2);
    expect(element.shadowRoot.querySelectorAll('.related-link')).toHaveLength(1);
    expect(caseRows(element)).toEqual(['New']);
});

it('drops old Case details when the visible parent changes and keeps the task after a failed Case query', async () => {
    const element = await renderBoard();
    emitTasks([firstTask]);
    await Promise.resolve();
    emitCases([practiceCaseDetails]);
    await Promise.resolve();
    expect(caseRows(element)).toContain('TRAIN-001');

    emitTasks([{ ...firstTask, What: differentCase }]);
    await Promise.resolve();
    graphql.emit({ errors: [{ message: 'Case query unavailable' }] }, matchesCases);
    await Promise.resolve();

    expect(element.shadowRoot.querySelectorAll('.task-card')).toHaveLength(1);
    expect(caseRows(element)).toEqual([]);
    expect(element.shadowRoot.textContent).toContain('Some case details are unavailable');
    expect(element.shadowRoot.textContent).not.toContain('Case query unavailable');
});

it('keeps a task without a visible parent and identifies the training cap', async () => {
    const element = await renderBoard();
    emitTasks([secondTask], true);
    await Promise.resolve();

    expect(element.shadowRoot.querySelectorAll('.task-card')).toHaveLength(1);
    expect(element.shadowRoot.querySelector('.related-link')).toBeNull();
    expect(element.shadowRoot.textContent).toContain('More tasks are available');
});

it('shows a task error and recovers on an explicit refresh', async () => {
    const element = await renderBoard();
    const refresh = jest.fn(async () => emitTasks([]));
    graphql.emit({ errors: [{ message: 'Task access denied' }], refresh }, matchesTasks);
    await Promise.resolve();

    expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toContain('Tasks could not be loaded');
    element.shadowRoot.querySelector('lightning-button[slot="actions"]').click();
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(refresh).toHaveBeenCalledTimes(1);
    expect(element.shadowRoot.textContent).toContain('No tasks to show');
});

it('shows usable Task rows and a notice when a partial result omits page information', async () => {
    const element = await renderBoard();
    const Task = { edges: [{ node: secondTask }, null], pageInfo: null };
    graphql.emit({
        data: { uiapi: { query: { Task } } },
        errors: [{ message: 'Page information unavailable' }]
    }, matchesTasks);
    await Promise.resolve();

    expect(element.shadowRoot.querySelectorAll('.task-card')).toHaveLength(1);
    expect(element.shadowRoot.textContent).toContain('Some tasks or related records could not be loaded');
    expect(element.shadowRoot.textContent).not.toContain('Page information unavailable');
});

it('shows a safe error when the Task connection contains no usable edges', async () => {
    const element = await renderBoard();
    const Task = { edges: null, pageInfo: null };
    graphql.emit({ data: { uiapi: { query: { Task } } } }, matchesTasks);
    await Promise.resolve();

    expect(element.shadowRoot.querySelector('[role="alert"]').textContent).toContain('Tasks could not be loaded');
    expect(element.shadowRoot.querySelector('.task-card')).toBeNull();
});

it('discards stale Case details if the same visible parent cannot refresh', async () => {
    const element = await renderBoard();
    const refreshTasks = jest.fn(async () => emitTasks([firstTask], false, refreshTasks));
    const refreshCases = jest.fn().mockRejectedValue(new Error('Case read failed'));
    emitTasks([firstTask], false, refreshTasks);
    await Promise.resolve();
    emitCases([practiceCaseDetails], refreshCases);
    await Promise.resolve();
    expect(caseRows(element)).toContain('TRAIN-001');

    element.shadowRoot.querySelector('lightning-button[slot="actions"]').click();
    await new Promise((resolve) => setTimeout(resolve, 0));

    expect(refreshTasks).toHaveBeenCalledTimes(1);
    expect(refreshCases).toHaveBeenCalledTimes(1);
    expect(element.shadowRoot.querySelectorAll('.task-card')).toHaveLength(1);
    expect(caseRows(element)).toEqual([]);
    expect(element.shadowRoot.textContent).toContain('Some case details are unavailable');
});
