import { useMemo } from 'react';
import { TodoInput } from './components/TodoInput';
import { TodoList } from './components/TodoList';
import { FilterButtons } from './components/FilterButtons';
import { Stats } from './components/Stats';
import { LanguageToggle } from './components/LanguageToggle';
import { useTodos } from './hooks/useTodos';
import { useFilter } from './hooks/useFilter';
import { useTranslation } from './hooks/useTranslation';
import './App.css';

function App() {
  const { t } = useTranslation();
  const { todos, addTodo, toggleTodo, deleteTodo, updateTodo } = useTodos();
  const { filter, setFilter } = useFilter();

  const filteredTodos = useMemo(() => {
    let result = todos;

    switch (filter) {
      case 'active':
        result = result.filter(t => !t.completed);
        break;
      case 'completed':
        result = result.filter(t => t.completed);
        break;
      case 'work':
      case 'personal':
      case 'study':
      case 'other':
        result = result.filter(t => t.category === filter);
        break;
    }

    return result;
  }, [todos, filter]);

  const stats = useMemo(() => ({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length,
  }), [todos]);

  return (
    <div className="app-container">
      <LanguageToggle />
      <h1 className="app-title">{t.app.title}</h1>

      <TodoInput onAdd={addTodo} />

      <FilterButtons currentFilter={filter} onFilterChange={setFilter} />

      <TodoList
        todos={filteredTodos}
        onToggle={toggleTodo}
        onDelete={deleteTodo}
        onUpdate={updateTodo}
      />

      <Stats stats={stats} />
    </div>
  );
}

export default App;
