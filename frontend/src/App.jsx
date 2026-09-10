import { useState } from 'react';

function App() {
  const [query, setQuery] = useState('');
  const [algorithm, setAlgorithm] = useState('bm25');
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [searchTime, setSearchTime] = useState(null);

  const handleSearch = async () => {
    const startTime = performance.now();

    const response = await fetch(
      `http://127.0.0.1:8000/api/v1/search?q=${query}&algorithm=${algorithm}`
    );
    const data = await response.json();

    const endTime = performance.now();

    setResults(data.results);
    setTotal(data.total);
    setSearchTime(Math.round(endTime - startTime));
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

      <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
        <option value="bm25">BM25</option>
        <option value="tfidf">TF-IDF</option>
      </select>

      <button onClick={handleSearch}>Search</button>

      {searchTime !== null && (
        <p>{total} results — {searchTime}ms — Algorithm: {algorithm.toUpperCase()}</p>
      )}

      <ul>
        {results.map((result) => (
          <li key={result.document_id}>
            <strong>{result.title}</strong>
            <p>{result.snippet}</p>
            <a href={result.url}>{result.url}</a>
            <p>Score: {result.score}</p>
            <p dangerouslySetInnerHTML={{ __html: result.snippet }}></p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;