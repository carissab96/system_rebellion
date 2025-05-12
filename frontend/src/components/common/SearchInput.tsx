import React, { useState, useEffect } from 'react';

interface SearchInputProps {
  onSearch: (term: string) => void;
  placeholder?: string;
  initialValue?: string;
  debounceTime?: number;
}

export const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  placeholder = 'Search...',
  initialValue = '',
  debounceTime = 300,
}) => {
  const [searchTerm, setSearchTerm] = useState(initialValue);

  useEffect(() => {
    const handler = setTimeout(() => {
      onSearch(searchTerm);
    }, debounceTime);

    return () => {
      clearTimeout(handler);
    };
  }, [searchTerm, onSearch, debounceTime]);

  return (
    <div className="search-input-container">
      <input
        type="text"
        className="search-input"
        placeholder={placeholder}
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      {searchTerm && (
        <button
          className="clear-search"
          onClick={() => setSearchTerm('')}
          aria-label="Clear search"
        >
          ×
        </button>
      )}
    </div>
  );
};
