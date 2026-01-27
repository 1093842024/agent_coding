export const enUS = {
  app: {
    title: 'My Todo List',
  },
  input: {
    placeholder: 'Add a new todo...',
    addButton: 'Add',
    category: {
      work: 'Work',
      personal: 'Personal',
      study: 'Study',
      other: 'Other',
    },
  },
  filter: {
    all: 'All',
    active: 'Active',
    completed: 'Completed',
  },
  todo: {
    edit: 'Edit',
    delete: 'Delete',
    save: 'Save',
    cancel: 'Cancel',
  },
  deadline: {
    overdue: (days: number) => `${days} day${days > 1 ? 's' : ''} overdue`,
    today: 'Due today',
    tomorrow: 'Due tomorrow',
    inDays: (days: number) => `Due in ${days} days`,
  },
  stats: {
    total: 'Total',
    active: 'Active',
    completed: 'Completed',
  },
  empty: {
    title: 'No todos yet',
    hint: 'Add a new task to get started!',
  },
  language: {
    switch: '中文',
    current: 'English',
  },
};
