import { useState, useEffect } from 'react';
import { Todo } from '../types';

const STORAGE_KEY = 'todos';

export function useTodos() {
  const [todos, setTodos] = useState<Todo[]>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos));
  }, [todos]);

  const addTodo = (text: string, category: string, deadline: string) => {
    const newTodo: Todo = {
      id: Date.now(),
      text,
      category: category as Todo['category'],
      deadline,
      completed: false,
      createdAt: new Date().toISOString(),
    };
    setTodos(prev => [newTodo, ...prev]);
  };

  const toggleTodo = (id: number) => {
    setTodos(prev =>
      prev.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  const deleteTodo = (id: number) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  };

  const updateTodo = (id: number, updates: Partial<Todo>) => {
    setTodos(prev =>
      prev.map(todo => (todo.id === id ? { ...todo, ...updates } : todo))
    );
  };

  return { todos, addTodo, toggleTodo, deleteTodo, updateTodo };
}
