export default function LearningPathTable() {
  const stored = localStorage.getItem("learningPath");
  const modules = stored ? JSON.parse(stored) : [];

  return (
    <div className="card">
      <h2>🎯 Your Personalized Learning Path</h2>

      {modules.length === 0 ? (
        <p>No modules found. Complete assessment to get recommendations.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Module</th>
              <th>Skill</th>
              <th>Level</th>
              <th>Link</th>
            </tr>
          </thead>
          <tbody>
            {modules.map((mod, idx) => (
              <tr key={mod.id || idx}>
                <td>{mod.title}</td>
                <td>{mod.skill}</td>
                <td
                  className={
                    mod.level === "Beginner"
                      ? "status-not-started"
                      : mod.level === "Intermediate"
                      ? "status-in-progress"
                      : "status-completed"
                  }
                >
                  {mod.level}
                </td>
                <td>
                  <a href={mod.url} target="_blank" rel="noopener noreferrer">
                    View
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
