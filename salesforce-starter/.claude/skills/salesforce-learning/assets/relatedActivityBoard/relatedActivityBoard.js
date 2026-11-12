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
                            WhatId @optional { value displayValue }
                        }
                    }
                    pageInfo { hasNextPage }
                }
            }
        }
    }
`;

const CASE_DETAILS_QUERY = gql`
    query RelatedActivityCaseDetails($parentIds: [ID!]!) {
        uiapi {
            query {
                Case(first: 50, where: { Id: { in: $parentIds } }) @optional {
                    edges {
                        node {
                            Id
                            Subject @optional { value }
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
    const parent = node.WhatId;
    return {
        id: node.Id,
        subject: node.Subject?.value ?? 'Untitled task',
        status: node.Status?.value ?? 'Status unavailable',
        statusLabel: node.Status?.displayValue ?? node.Status?.value ?? 'Status unavailable',
        priority: node.Priority?.displayValue ?? node.Priority?.value,
        dueDate: node.ActivityDate?.value,
        related: parent?.value ? { id: parent.value, label: parent.displayValue } : undefined
    };
}

export default class RelatedActivityBoard extends NavigationMixin(LightningElement) {
    @api showCaseNumber = false;
    @api showCaseStatus = false;
    @api showCasePriority = false;

    tasks = [];
    caseDetails = new Map();
    parentIds = [];
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
        const edges = data?.uiapi?.query?.Case?.edges;
        const visibleIds = new Set(this.parentIds);
        this.caseDetails = new Map(
            (Array.isArray(edges) ? edges : []).filter((edge) => visibleIds.has(edge?.node?.Id)).map(({ node }) => [node.Id, node])
        );
        this.casePartial = Boolean(errors?.length) || !Array.isArray(edges);
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

        // The Case query returns only matching, accessible Cases from these parent IDs.
        const ids = [...new Set(this.tasks.map(({ related }) => related?.id).filter(Boolean))].sort();

        if (ids.join(',') !== this.parentIds.join(',')) {
            this.parentIds = ids;
            this.caseVariables = ids.length ? { parentIds: ids } : undefined;
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
            const related = task.related && {
                id: task.related.id,
                label: details?.Subject?.value || task.related.label || 'Open related record'
            };
            group.cards.push({ ...task, related, caseRows });
            groups.set(task.status, group);
        }
        return [...groups.values()];
    }

    async refreshBoard() {
        const previousCaseVariables = this.caseVariables;
        this.refreshing = true;
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
        const attributes = { recordId, actionName: 'view' };
        if (objectApiName) {
            attributes.objectApiName = objectApiName;
        }
        this[NavigationMixin.Navigate]({ type: 'standard__recordPage', attributes });
    }
}
