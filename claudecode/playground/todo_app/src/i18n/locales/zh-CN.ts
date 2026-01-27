export const zhCN = {
  app: {
    title: '我的待办事项',
  },
  input: {
    placeholder: '添加新的待办事项...',
    addButton: '添加',
    category: {
      work: '工作',
      personal: '个人',
      study: '学习',
      other: '其他',
    },
  },
  filter: {
    all: '全部',
    active: '未完成',
    completed: '已完成',
  },
  todo: {
    edit: '编辑',
    delete: '删除',
    save: '保存',
    cancel: '取消',
  },
  deadline: {
    overdue: (days: number) => `已过期 ${days} 天`,
    today: '今天到期',
    tomorrow: '明天到期',
    inDays: (days: number) => `${days} 天后到期`,
  },
  stats: {
    total: '总计',
    active: '未完成',
    completed: '已完成',
  },
  empty: {
    title: '暂无待办事项',
    hint: '添加一个新任务开始吧！',
  },
  language: {
    switch: 'English',
    current: '中文',
  },
};
