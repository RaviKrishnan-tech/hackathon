export default function Leaderboard() {
  const leaderboard = [
    { rank: 1, name: "Alice", score: 98 },
    { rank: 2, name: "Bob", score: 95 },
    { rank: 3, name: "Charlie", score: 90 },
  ];

  return (
    <div className="card">
      <h2>Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Name</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((user, idx) => (
            <tr key={idx}>
              <td className="text-center">{user.rank}</td>
              <td>{user.name}</td>
              <td className="text-center">{user.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
