import { api, LightningElement, wire } from 'lwc';
import { gql, graphql } from 'lightning/graphql';
import { NavigationMixin } from 'lightning/navigation';

const TASKS_QUERY = gql`
    query RelatedActivityTasks {
        uiapi {
            query {
                Task(first: 50, orderBy: { Status: { order: ASC }, Id: { order: ASC } }) {
                    edges {
                        node {
                            Id
                            Subject { value }
                            Status { value displayValue }
                            Priority @optional { value displayValue }
                            ActivityDate @optional { value }
                            What @optional {
                                ... on Record {
                                    Id
                                    ApiName
                                    DisplayValue @optional
                                }
                            }
                        }
                    }
                    pageInfo { hasNextPage }
                }
            }
        }
    }
`;

const CASE_DETAILS_QUERY = gql`
    query RelatedActivityCaseDetails($caseIds: [ID!]!) {
        uiapi {
            query {
                Case(first: 50, where: { Id: { in: $caseIds } }) @optional {
                    edges {
                        node {
                            Id
                            CaseNumber @optional { value }
                            Status @optional { value displayValue }
                            Priority @optional { value displayValue }
                        }
                    }
                }
            }
        }
    }
`;

const CASE_FIELDS = [
    { key: 'CaseNumber', label: 'Case number', setting: 'showCaseNumber' },
    { key: 'Status', label: 'Case status', setting: 'showCaseStatus' },
    { key: 'Priority', label: 'Case priority', setting: 'showCasePriority' }
];

function toCard({ node }) {
    const parent = node.What;
    return {
        id: node.Id,
        subject: node.Subject?.value ?? 'Untitled task',
        status: node.Status?.value ?? 'Status unavailable',
        statusLabel: node.Status?.displayValue ?? node.Status?.value ?? 'Status unavailable',
        priority: node.Priority?.displayValue ?? node.Priority?.value,
        dueDate: node.ActivityDate?.value,
        related: parent?.Id && parent.ApiName
            ? {
                id: parent.Id,
                objectApiName: parent.ApiName,
                label: typeof parent.DisplayValue === 'string' && parent.DisplayValue
                    ? parent.DisplayValue
                    : 'Open related record'
            }
            : undefined
    };
}

export default class RelatedActivityBoard extends NavigationMixin(LightningElement) {
    @api showCaseNumber = false;
    @api showCaseStatus = false;
    @api showCasePriority = false;

    tasks = [];
    caseDetails = new Map();
    caseIds = [];
    caseVariables;
    refreshTasks;
    refreshCases;
    initialLoad = true;
    refreshing = false;
    taskError = false;
    taskPartial = false;
    caseLoading = false;
    casePartial = false;
    hasMoreTasks = false;

    @wire(graphql, { query: TASKS_QUERY })
    receiveTasks({ data, errors, refresh }) {
        this.refreshTasks = refresh ?? this.refreshTasks;
        if (!data && !errors?.length) {
            return;
        }

        const page = data?.uiapi?.query?.Task;
        this.updateTasks(page, Boolean(errors?.length));
    }

    get caseQuery() {
        return this.caseVariables ? CASE_DETAILS_QUERY : undefined;
    }

    @wire(graphql, { query: '$caseQuery', variables: '$caseVariables' })
    receiveCases({ data, errors, refresh }) {
        if (!this.caseVariables || (!data && !errors?.length)) {
            return;
        }
        this.refreshCases = refresh ?? this.refreshCases;
        const edges = data?.uiapi?.query?.Case?.edges ?? [];
        const visibleIds = new Set(this.caseIds);
        this.caseDetails = new Map(
            edges.filter((edge) => visibleIds.has(edge?.node?.Id)).map(({ node }) => [node.Id, node])
        );
        this.casePartial = Boolean(errors?.length) || this.caseDetails.size < this.caseIds.length;
        this.caseLoading = false;
    }

    updateTasks(page, hasErrors) {
        const edges = page?.edges;
        const hasTaskRows = Array.isArray(edges);
        this.initialLoad = false;
        this.taskError = !hasTaskRows;
        this.taskPartial = hasTaskRows && (hasErrors || !page.pageInfo);
        this.tasks = hasTaskRows ? edges.filter((edge) => edge?.node?.Id).map(toCard) : [];
        this.hasMoreTasks = page?.pageInfo?.hasNextPage ?? false;

        const ids = [...new Set(this.tasks
            .filter(({ related }) => related?.objectApiName === 'Case')
            .map(({ related }) => related.id))].sort();

        if (ids.join(',') !== this.caseIds.join(',')) {
            this.caseIds = ids;
            this.caseVariables = ids.length ? { caseIds: ids } : undefined;
            this.caseDetails = new Map();
            this.refreshCases = undefined;
            this.caseLoading = ids.length > 0;
            this.casePartial = false;
        }
    }

    get loading() {
        return this.initialLoad || this.refreshing;
    }

    get canRefresh() {
        return Boolean(this.refreshTasks);
    }

    get hasTasks() {
        return this.tasks.length > 0;
    }

    get taskCount() {
        return this.tasks.length;
    }

    get columns() {
        const groups = new Map();
        for (const task of this.tasks) {
            const group = groups.get(task.status) ?? {
                key: task.status,
                label: task.statusLabel,
                cards: []
            };
            const details = this.caseDetails.get(task.related?.id);
            const caseRows = CASE_FIELDS
                .filter(({ key, setting }) => this[setting] && details?.[key]?.value != null)
                .map(({ key, label }) => ({
                    key,
                    label,
                    value: details[key].displayValue ?? details[key].value
                }));
            group.cards.push({ ...task, caseRows });
            groups.set(task.status, group);
        }
        return [...groups.values()];
    }

    async refreshBoard() {
        const previousCaseVariables = this.caseVariables;
        this.refreshing = true;
        this.caseDetails = new Map();
        this.casePartial = this.caseIds.length > 0;
        try {
            await this.refreshTasks();
        } catch {
            this.updateTasks(undefined, true);
        }

        if (this.caseVariables && this.caseVariables === previousCaseVariables && this.refreshCases) {
            try {
                await this.refreshCases();
            } catch {
                this.caseDetails = new Map();
                this.caseLoading = false;
                this.casePartial = true;
            }
        }
        this.refreshing = false;
    }

    openRecord(event) {
        const { recordId, objectApiName } = event.currentTarget.dataset;
        this[NavigationMixin.Navigate]({
            type: 'standard__recordPage',
            attributes: { recordId, objectApiName, actionName: 'view' }
        });
    }
}
