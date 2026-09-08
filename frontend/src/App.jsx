import { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await fetch(`http://127.0.0.1:8000/api/v1/search?q=${query}`);
    const data = await response.json();
    setResults(data.results);
  };

  return (
    <div>
      <h1>OpenSearch</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search..."
      />
      <button onClick={handleSearch}>Search</button>

      <ul>
        {results.map((result) => (
          <li key={result.document_id}>
            <strong>{result.title}</strong>
            <p>{result.snippet}</p>
            <a href={result.url}>{result.url}</a>
            <p>Score: {result.score}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;