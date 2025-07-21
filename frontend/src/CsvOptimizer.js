import React, { useState } from "react";
import axios from "axios";

const constraintOps = [
  { label: "≤", value: "<=" },
  { label: "≥", value: ">=" },
  { label: "=", value: "==" },
  { label: "<", value: "<" },
  { label: ">", value: ">" },
];

export default function CsvOptimizer() {
  const [csvFile, setCsvFile] = useState(null);
  const [filename, setFilename] = useState("");
  const [headers, setHeaders] = useState([]);
  const [preview, setPreview] = useState([]);
  const [objectiveCol, setObjectiveCol] = useState("");
  const [maximize, setMaximize] = useState(true);

  const [constraintCol, setConstraintCol] = useState("");
  const [constraintOp, setConstraintOp] = useState("<=");
  const [constraintVal, setConstraintVal] = useState("");

  const [population, setPopulation] = useState(50);
  const [generations, setGenerations] = useState(30);
  const [mutation, setMutation] = useState(0.1);

  const [result, setResult] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  // Handle CSV upload
  const handleFileChange = (e) => {
    setCsvFile(e.target.files[0]);
    setHeaders([]);
    setPreview([]);
    setFilename("");
    setObjectiveCol("");
    setConstraintCol("");
    setResult(null);
    setPlotUrl(null);
  };

  const uploadCsv = async () => {
    if (!csvFile) return;
    const data = new FormData();
    data.append("file", csvFile);
    // Use env-aware base URL if available, fallback to relative
    const API_BASE = process.env.REACT_APP_API_BASE || "";
    const res = await axios.post(`${API_BASE}/api/upload_csv`, data);
    setHeaders(res.data.headers);
    setFilename(res.data.filename);
    setPreview(res.data.preview);
    setObjectiveCol(res.data.headers[0]);
    setConstraintCol("");
    setResult(null);
    setPlotUrl(null);
    alert("CSV uploaded! Columns: " + res.data.headers.join(", "));
  };

  // Run optimizer
  const runOptimizer = async () => {
    setLoading(true);
    setResult(null);
    setPlotUrl(null);
    const API_BASE = process.env.REACT_APP_API_BASE || "";
    try {
      const params = {
        csv_filename: filename,
        objective_col: objectiveCol,
        maximize,
        constraint_col: constraintCol || null,
        constraint_op: constraintCol ? constraintOp : null,
        constraint_val: constraintCol ? constraintVal : null,
        population_size: population,
        generations,
        mutation_rate: mutation,
      };
      const res = await axios.post(
        `${API_BASE}/api/run_problem/csv_optimizer`,
        params
      );
      setResult(res.data.result);
      if (res.data.plotFilename) {
        setPlotUrl(`${API_BASE}/api/plot/${res.data.plotFilename}?t=${Date.now()}`);
      }
    } catch (e) {
      alert("Error running optimizer: " + (e.response?.data?.error || e.message));
    }
    setLoading(false);
  };

  return (
    <div
      style={{
        margin: "80px auto",
        padding: "56px 0",
        background: "#23293a",
        borderRadius: 22,
        maxWidth: 950,
        minWidth: 400,
        boxShadow: "0 4px 24px #0008",
        display: "flex",
        flexDirection: "column",
        alignItems: "center"
      }}
    >
      <h2 style={{
        fontSize: "2.6rem",
        fontWeight: 800,
        marginBottom: 40,
        color: "#fff",
        textAlign: "center"
      }}>
        Upload a CSV for Optimization
      </h2>
      <div style={{ marginBottom: 32 }}>
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          style={{
            fontSize: "1.2rem",
            padding: "10px 18px",
            borderRadius: 5,
            border: "1px solid #444",
            background: "#2c3245",
            color: "#fff"
          }}
        />
        <button
          onClick={uploadCsv}
          disabled={!csvFile}
          style={{
            fontSize: "1.2rem",
            fontWeight: 700,
            padding: "10px 34px",
            marginLeft: 18,
            borderRadius: 6,
            border: "none",
            background: "#90caf9",
            color: "#23293a",
            cursor: csvFile ? "pointer" : "not-allowed",
            opacity: csvFile ? 1 : 0.5
          }}
        >
          Upload CSV
        </button>
      </div>

      {headers.length > 0 && (
        <div style={{ width: "100%", maxWidth: 800, display: "flex", flexDirection: "column", alignItems: "center" }}>
          <h3 style={{ fontSize: "1.7rem", fontWeight: 700, marginBottom: 16 }}>Preview:</h3>
          <div style={{ width: "100%", overflowX: "auto", marginBottom: 24 }}>
            <table style={{ background: "#222", color: "#fff", margin: "0 auto", borderRadius: 8, fontSize: "1.15rem", minWidth: 500 }}>
              <thead>
                <tr>{headers.map(h => <th key={h} style={{ padding: "7px 22px" }}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {preview.map((row, i) =>
                  <tr key={i}>{headers.map(h => <td key={h} style={{ padding: "7px 22px" }}>{row[h]}</td>)}</tr>
                )}
              </tbody>
            </table>
          </div>

          <h3 style={{ fontSize: "1.6rem", fontWeight: 700, margin: "28px 0 16px" }}>Setup Optimization</h3>
          <div style={{ marginBottom: 18, fontSize: "1.18rem", display: "flex", alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ marginRight: 18 }}>
              Objective Column:&nbsp;
              <select value={objectiveCol} onChange={e => setObjectiveCol(e.target.value)} style={{ fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5 }}>
                {headers.map(h => <option value={h} key={h}>{h}</option>)}
              </select>
            </label>
            <label style={{ marginRight: 18 }}>
              <input
                type="checkbox"
                checked={maximize}
                onChange={e => setMaximize(e.target.checked)}
                style={{ transform: "scale(1.3)", marginRight: 8 }}
              /> Maximize (uncheck for Minimize)
            </label>
          </div>
          <div style={{ marginBottom: 18, fontSize: "1.18rem", display: "flex", alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ marginRight: 10 }}>
              Constraint Column:&nbsp;
              <select
                value={constraintCol}
                onChange={e => setConstraintCol(e.target.value)}
                style={{ fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5 }}
              >
                <option value="">None</option>
                {headers
                  .filter(h => h !== objectiveCol)
                  .map(h => <option value={h} key={h}>{h}</option>)}
              </select>
            </label>
            {constraintCol &&
              <>
                <select value={constraintOp} onChange={e => setConstraintOp(e.target.value)} style={{ fontSize: "1.1rem", marginLeft: 12, marginRight: 8, padding: "4px 10px", borderRadius: 5 }}>
                  {constraintOps.map(op => (
                    <option value={op.value} key={op.value}>{op.label}</option>
                  ))}
                </select>
                <input
                  type="number"
                  value={constraintVal}
                  onChange={e => setConstraintVal(e.target.value)}
                  style={{ width: 100, fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5, marginLeft: 8 }}
                  placeholder="Value"
                />
              </>
            }
          </div>
          <div style={{ marginBottom: 18, fontSize: "1.18rem", display: "flex", alignItems: "center", flexWrap: "wrap" }}>
            <label style={{ marginRight: 18 }}>
              Population Size:&nbsp;
              <input
                type="number"
                min={2}
                max={500}
                value={population}
                onChange={e => setPopulation(Number(e.target.value))}
                style={{ width: 80, fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5 }}
              />
            </label>
            <label style={{ marginRight: 18 }}>
              Generations:&nbsp;
              <input
                type="number"
                min={1}
                max={1000}
                value={generations}
                onChange={e => setGenerations(Number(e.target.value))}
                style={{ width: 80, fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5 }}
              />
            </label>
            <label>
              Mutation Rate:&nbsp;
              <input
                type="number"
                min={0}
                max={1}
                step={0.01}
                value={mutation}
                onChange={e => setMutation(Number(e.target.value))}
                style={{ width: 80, fontSize: "1.1rem", padding: "4px 10px", borderRadius: 5 }}
              />
            </label>
          </div>
          <button
            onClick={runOptimizer}
            disabled={loading}
            style={{
              background: "#90caf9",
              color: "#222",
              fontWeight: 700,
              border: "none",
              borderRadius: 8,
              padding: "12px 38px",
              marginBottom: 18,
              marginTop: 8,
              cursor: loading ? "not-allowed" : "pointer",
              fontSize: "1.2rem",
              boxShadow: "0 2px 12px #0004"
            }}
          >
            {loading ? "Optimizing..." : "Run Optimizer"}
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{
          marginTop: 40,
          background: "#161b24",
          padding: 30,
          borderRadius: 12,
          maxWidth: 820,
          width: "100%",
          fontSize: "1.2rem",
          color: "#fff",
          boxShadow: "0 2px 12px #0004"
        }}>
          <h3 style={{ fontWeight: 700, marginBottom: 10 }}>Result</h3>
          {result.best_score !== undefined && (
            <div style={{ marginBottom: 8 }}>
              <b>Best Score:</b> {result.best_score}
            </div>
          )}
          {result.best && (
            <div style={{ wordBreak: "break-all", marginBottom: 8 }}>
              <b>Best Solution:</b>
              <pre style={{
                background: "#23293a",
                padding: "12px 18px",
                borderRadius: 6,
                fontSize: "1.1rem",
                marginTop: 5,
                color: "#e3f2fd"
              }}>{JSON.stringify(result.best, null, 2)}</pre>
            </div>
          )}
          {result.history && (
            <div style={{ marginTop: 18 }}>
              <b>Fitness by Generation:</b>
              <div style={{
                maxHeight: 180,
                overflowY: "auto",
                background: "#23293a",
                borderRadius: 4,
                fontSize: 15,
                padding: 10,
                marginTop: 6,
                marginBottom: 10
              }}>
                {result.history.map((fit, i) =>
                  <div key={i}>Gen {i + 1}: {fit}</div>
                )}
              </div>
            </div>
          )}
          {plotUrl && (
            <div style={{ marginTop: 18, display: "flex", justifyContent: "center", alignItems: "center" }}>
              <img src={plotUrl} alt="Fitness Progress" style={{ maxWidth: "100%", borderRadius: 8 }} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}