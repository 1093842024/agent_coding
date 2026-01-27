export type Category = 'work' | 'personal' | 'study' | 'other';

export type Filter = 'all' | 'active' | 'completed' | Category;

export interface Todo {
  id: number;
  text: string;
  category: Category;
  deadline: string;
  completed: boolean;
  createdAt: string;
}

export interface TodoStats {
  total: number;
  active: number;
  completed: number;
}
