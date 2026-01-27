import { useState } from 'react';
import { Filter } from '../types';

export function useFilter() {
  const [filter, setFilter] = useState<Filter>('all');

  return { filter, setFilter };
}
