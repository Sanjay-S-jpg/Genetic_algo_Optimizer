import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  IconButton,
  Tooltip,
  Snackbar,
  Alert,
  CircularProgress,
  Slider,
  Input,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Fade,
} from "@mui/material";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import DownloadIcon from "@mui/icons-material/Download";
import ShareIcon from "@mui/icons-material/Share";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import HelpOutlineIcon from "@mui/icons-material/HelpOutline";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#90caf9" },
    secondary: { main: "#f48fb1" },
    background: { default: "#181c24", paper: "#23293a" },
    text: { primary: "#fff" },
  },
  shape: { borderRadius: 12 },
  typography: { fontFamily: "Montserrat, Arial, sans-serif" },
  components: {
    MuiSlider: {
      styleOverrides: {
        root: {
          height: 8,
        },
        thumb: {
          width: 24,
          height: 24,
        },
        track: {
          height: 8,
          borderRadius: 4,
        },
        rail: {
          height: 8,
          borderRadius: 4,
        },
      },
    },
    MuiInput: {
      styleOverrides: {
        input: {
          fontSize: 18,
          fontWeight: 600,
          textAlign: "center",
          padding: "7px 0",
        },
      },
    },
  },
});

function App() {
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [paramFields, setParamFields] = useState([]);
  const [params, setParams] = useState({});
  const [result, setResult] = useState(null);
  const [plotUrl, setPlotUrl] = useState(null);

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [alert, setAlert] = useState({ open: false, msg: "", type: "info" });
  const [running, setRunning] = useState(false);
  const [shareDialog, setShareDialog] = useState(false);

  useEffect(() => {
    fetchProblems();
  }, []);

  const fetchProblems = async () => {
    const res = await axios.get("http://127.0.0.1:5000/api/problems");
    setProblems(res.data);
  };

  const handleProblemUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadError("");
    const formData = new FormData();
    formData.append("file", file);
    try {
      await axios.post("http://127.0.0.1:5000/api/upload_problem", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAlert({ open: true, msg: "Problem uploaded!", type: "success" });
      await fetchProblems();
    } catch (err) {
      setUploadError(err?.response?.data?.error || "Upload failed");
      setAlert({ open: true, msg: "Upload failed", type: "error" });
    } finally {
      setUploading(false);
    }
  };

  const handleProblemSelect = (problem) => {
    setSelectedProblem(problem);
    setResult(null);
    setPlotUrl(null);
    axios.get(`http://127.0.0.1:5000/api/problem_params/${problem.id}`).then((res) => {
      setParamFields(res.data);
      const defaults = {};
      res.data.forEach((field) => (defaults[field.name] = field.default));
      setParams(defaults);
    });
  };

  const handleParamChange = (name, value) => {
    setParams({ ...params, [name]: value });
  };

  const handleRun = async (e) => {
    e.preventDefault();
    setResult(null);
    setPlotUrl(null);
    setRunning(true);
    try {
      const res = await axios.post(
        `http://127.0.0.1:5000/api/run_problem/${selectedProblem.id}`,
        params
      );
      setResult(res.data.result);
      setPlotUrl(
        `http://127.0.0.1:5000/api/plot/${res.data.plotFilename}?t=${Date.now()}`
      );
      setAlert({ open: true, msg: "Run complete!", type: "success" });
    } catch (err) {
      setAlert({ open: true, msg: "Run failed!", type: "error" });
    }
    setRunning(false);
  };

  const handleDownloadSolution = async () => {
    if (!selectedProblem) return;
    const res = await axios.post(
      `http://127.0.0.1:5000/api/download_solution/${selectedProblem.id}`,
      params,
      { responseType: "blob" }
    );
    const url = window.URL.createObjectURL(
      new Blob([res.data], { type: "application/json" })
    );
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${selectedProblem.id}_solution.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handleDownloadPlot = () => {
    if (!plotUrl) return;
    const cleanUrl = plotUrl.split("?")[0];
    const downloadUrl = `${cleanUrl}?download=1`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.setAttribute("download", cleanUrl.split("/").pop());
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handleSuggestParams = () => {
    const suggested = {};
    paramFields.forEach((field) => {
      if (field.name === "population_size") suggested[field.name] = 100;
      else if (field.name === "mutation_rate") suggested[field.name] = 0.05;
      else if (field.name === "generations") suggested[field.name] = 200;
      else if (field.default !== undefined) suggested[field.name] = field.default;
      else suggested[field.name] = "";
    });
    setParams(suggested);
    setAlert({ open: true, msg: "Suggested parameters loaded!", type: "info" });
  };

  const handleCopyShareLink = () => {
    const state = { p: selectedProblem.id, params };
    const shareUrl = `${window.location.origin}${window.location.pathname}#${encodeURIComponent(
      JSON.stringify(state)
    )}`;
    navigator.clipboard.writeText(shareUrl);
    setShareDialog(false);
    setAlert({ open: true, msg: "Shareable link copied!", type: "success" });
  };

  useEffect(() => {
    if (window.location.hash.length > 5) {
      try {
        const data = JSON.parse(
          decodeURIComponent(window.location.hash.slice(1))
        );
        if (data.p && data.params) {
          axios.get("http://127.0.0.1:5000/api/problems").then((res) => {
            setProblems(res.data);
            const found = res.data.find((x) => x.id === data.p);
            if (found) {
              setSelectedProblem(found);
              axios
                .get(`http://127.0.0.1:5000/api/problem_params/${found.id}`)
                .then((res2) => {
                  setParamFields(res2.data);
                  setParams(data.params);
                });
            }
          });
        }
      } catch (e) {}
    }
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <AppBar position="static" color="default" elevation={2} sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h5" sx={{ flexGrow: 1 }}>
            Genetic Algorithm Optimizer
          </Typography>
          <Tooltip title="Upload a custom problem (.py)">
            <label>
              <input
                type="file"
                accept=".py"
                style={{ display: "none" }}
                onChange={handleProblemUpload}
                disabled={uploading}
              />
              <IconButton component="span" color="secondary" size="large">
                <UploadFileIcon />
              </IconButton>
            </label>
          </Tooltip>
        </Toolbar>
      </AppBar>
      <Snackbar
        open={alert.open}
        autoHideDuration={2500}
        onClose={() => setAlert({ ...alert, open: false })}
        anchorOrigin={{ vertical: "top", horizontal: "center" }}
      >
        <Alert severity={alert.type} variant="filled" sx={{ width: "100%" }}>
          {alert.msg}
        </Alert>
      </Snackbar>
      <Container
        maxWidth="lg"
        sx={{
          mb: 6,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: selectedProblem ? "flex-start" : "center",
          minHeight: selectedProblem ? "unset" : "70vh",
        }}
      >
        {/* Problem Selection: Centered and spaced */}
        {selectedProblem === null ? (
          <Fade in>
            <Box
              sx={{
                width: "100%",
                textAlign: "center",
                mt: 8,
              }}
            >
              <Typography variant="h4" sx={{ mb: 3, fontWeight: 600, letterSpacing: 1 }}>
                Select a Problem
              </Typography>
              <Grid
                container
                spacing={4}
                justifyContent="center"
                alignItems="center"
                sx={{ mb: 8 }}
              >
                {problems.map((prob) => (
                  <Grid item xs={12} sm={6} md={4} lg={3} key={prob.id}>
                    <Card
                      sx={{
                        minHeight: 120,
                        minWidth: 220,
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        border:
                          prob.name.includes("Custom") &&
                          "2px solid #f48fb1",
                        transition: "box-shadow 0.2s, border 0.2s",
                        boxShadow: 2,
                        "&:hover": {
                          boxShadow: 8,
                          borderColor: "#90caf9",
                          transform: "scale(1.04)",
                          cursor: "pointer",
                        },
                        background: "#222736",
                      }}
                      onClick={() => handleProblemSelect(prob)}
                    >
                      <CardContent>
                        <Typography
                          variant="h6"
                          color="primary"
                          gutterBottom
                          sx={{ fontWeight: 700, fontSize: 22, mb: 1 }}
                        >
                          {prob.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {prob.id.startsWith("custom:")
                            ? "User-uploaded Python module"
                            : "Built-in Problem"}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              {uploadError && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {uploadError}
                </Alert>
              )}
              {/* Extra: Home info, features, footer */}
              <Box sx={{ mt: 12, opacity: 0.7 }}>
                <Typography variant="subtitle1">
                  🧬 Try genetic optimization on classic and custom problems, right in your browser.<br />
                  <span style={{ color: "#90caf9" }}>Upload</span> your own problem in Python, <span style={{ color: "#f48fb1" }}>share</span> solutions with friends, and <span style={{ color: "#b0f49a" }}>visualize</span> GA performance!
                </Typography>
                <Typography variant="caption" sx={{ mt: 2, display: "block" }}>
                  Made with <span style={{ color: "#f48fb1" }}>♥</span> and React + Material UI
                </Typography>
              </Box>
            </Box>
          </Fade>
        ) : (
          <Fade in>
            <Box sx={{ width: "100%", maxWidth: "1050px", mx: "auto", mt: 2 }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
                <IconButton
                  color="secondary"
                  onClick={() => setSelectedProblem(null)}
                  size="large"
                  sx={{ mr: 1 }}
                >
                  <ArrowBackIcon />
                </IconButton>
                <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 700 }}>
                  {selectedProblem.name}
                </Typography>
              </Box>
              <Card
                sx={{
                  mb: 3,
                  background: "#20232f",
                  boxShadow: 6,
                  px: { xs: 1, md: 4 },
                  py: { xs: 2, md: 3 },
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                }}
              >
                <CardContent sx={{ width: "100%" }}>
                  <form onSubmit={handleRun}>
                    <Grid
                      container
                      spacing={2}
                      justifyContent="center"
                      alignItems="center"
                      sx={{ mb: 1 }}
                    >
                      {paramFields.map((field) => (
                        <Grid
                          item
                          xs={12}
                          sm={6}
                          md={2.4}
                          key={field.name}
                          sx={{
                            display: "flex",
                            flexDirection: "column",
                            alignItems: "center",
                          }}
                        >
                          <Typography
                            variant="subtitle2"
                            color="secondary"
                            sx={{
                              mb: 0.5,
                              display: "flex",
                              alignItems: "center",
                              fontWeight: 600,
                              fontSize: 15,
                              letterSpacing: 0.5,
                            }}
                          >
                            {field.label}
                            <Tooltip title={field.label}>
                              <HelpOutlineIcon
                                fontSize="small"
                                sx={{ ml: 0.5, opacity: 0.7 }}
                              />
                            </Tooltip>
                          </Typography>
                          <Box
                            sx={{
                              width: { xs: "98%", sm: 120, md: 180 },
                              display: "flex",
                              flexDirection: "column",
                              alignItems: "center",
                              gap: 1,
                            }}
                          >
                            {field.type === "number" ? (
                              <>
                                <Slider
                                  min={
                                    typeof field.min !== "undefined"
                                      ? field.min
                                      : field.name === "mutation_rate"
                                      ? 0
                                      : 1
                                  }
                                  max={
                                    typeof field.max !== "undefined"
                                      ? field.max
                                      : field.name === "generations"
                                      ? 1000
                                      : 500
                                  }
                                  step={
                                    typeof field.step !== "undefined"
                                      ? Number(field.step)
                                      : field.name === "mutation_rate"
                                      ? 0.01
                                      : 1
                                  }
                                  value={Number(params[field.name])}
                                  onChange={(e, v) =>
                                    handleParamChange(field.name, v)
                                  }
                                  valueLabelDisplay="on"
                                  sx={{
                                    width: { xs: 100, sm: 120, md: 160 },
                                    mb: -1.2,
                                  }}
                                  disabled={running}
                                  color="primary"
                                />
                                <Input
                                  type="number"
                                  value={params[field.name]}
                                  onChange={(e) =>
                                    handleParamChange(
                                      field.name,
                                      e.target.value === ""
                                        ? ""
                                        : Number(e.target.value)
                                    )
                                  }
                                  inputProps={{
                                    min:
                                      typeof field.min !== "undefined"
                                        ? field.min
                                        : field.name === "mutation_rate"
                                        ? 0
                                        : 1,
                                    max:
                                      typeof field.max !== "undefined"
                                        ? field.max
                                        : field.name === "generations"
                                        ? 1000
                                        : 500,
                                    step:
                                      typeof field.step !== "undefined"
                                        ? Number(field.step)
                                        : field.name === "mutation_rate"
                                        ? 0.01
                                        : 1,
                                    style: {
                                      width: 60,
                                      textAlign: "center",
                                    },
                                  }}
                                  disabled={running}
                                />
                              </>
                            ) : (
                              <Input
                                type={field.type}
                                name={field.name}
                                value={params[field.name]}
                                step={field.step || undefined}
                                onChange={(e) =>
                                  handleParamChange(field.name, e.target.value)
                                }
                                fullWidth
                                disabled={running}
                              />
                            )}
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                    <CardActions
                      sx={{
                        mt: 3,
                        justifyContent: "center",
                        gap: 2,
                        flexWrap: "wrap",
                      }}
                    >
                      <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        size="large"
                        sx={{
                          fontWeight: 700,
                          px: 4,
                          borderRadius: 3,
                          letterSpacing: 1.2,
                        }}
                        disabled={running}
                      >
                        {running ? (
                          <CircularProgress size={22} color="inherit" />
                        ) : (
                          "Run Optimizer"
                        )}
                      </Button>
                      <Button
                        variant="outlined"
                        color="secondary"
                        size="large"
                        onClick={handleSuggestParams}
                        sx={{
                          fontWeight: 700,
                          px: 3,
                          borderRadius: 3,
                          letterSpacing: 1.1,
                        }}
                        disabled={running}
                      >
                        Suggest Parameters
                      </Button>
                      <Button
                        variant="outlined"
                        color="info"
                        startIcon={<ShareIcon />}
                        size="large"
                        sx={{
                          fontWeight: 700,
                          px: 3,
                          borderRadius: 3,
                          letterSpacing: 1.1,
                        }}
                        onClick={() => setShareDialog(true)}
                        disabled={running}
                      >
                        Share
                      </Button>
                    </CardActions>
                  </form>
                </CardContent>
              </Card>
              {/* Results Section */}
              {result && (
                <Card sx={{ mb: 3, background: "#20232f", boxShadow: 4 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Result
                    </Typography>
                    {result.best_distance !== undefined ? (
                      <Typography>
                        <b>Best Distance:</b> {result.best_distance}
                      </Typography>
                    ) : (
                      <Typography>
                        <b>Best Score:</b> {result.score}
                      </Typography>
                    )}
                    <Typography sx={{ wordBreak: "break-all" }}>
                      <b>Best Solution:</b> {JSON.stringify(result.best)}
                    </Typography>
                    {/* Fitness Table */}
                    {result.history && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle1" gutterBottom>
                          Fitness Progress by Generation
                        </Typography>
                        <Box
                          sx={{
                            maxHeight: 260,
                            overflowY: "auto",
                            background: "#23293a",
                            borderRadius: 2,
                          }}
                        >
                          <table
                            style={{
                              width: "100%",
                              borderCollapse: "collapse",
                              color: "#fff",
                            }}
                          >
                            <thead>
                              <tr>
                                <th>Generation</th>
                                <th>Best Fitness</th>
                              </tr>
                            </thead>
                            <tbody>
                              {result.history.map((fitness, idx) => (
                                <tr key={idx}>
                                  <td>{idx + 1}</td>
                                  <td>{fitness}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </Box>
                      </Box>
                    )}
                    {/* Plot */}
                    {plotUrl && (
  <Box sx={{ mt: 2, display: "flex", flexDirection: "column", alignItems: "center" }}>
    <img
      src={plotUrl}
      alt="Fitness Progress"
      style={{ maxWidth: "100%", borderRadius: 8 }}
    />
    <Button
      variant="outlined"
      color="secondary"
      startIcon={<DownloadIcon />}
      onClick={handleDownloadPlot}
      sx={{ mt: 2, mb: 1, alignSelf: "flex-start" }}
    >
      Download Plot (PNG)
    </Button>
  </Box>
)}
                    {/* Download Solution */}
                    <Button
                      variant="contained"
                      color="secondary"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownloadSolution}
                      sx={{ mt: 1 }}
                    >
                      Download Solution (JSON)
                    </Button>
                    {/* Explanation */}
                    <Box
                      sx={{
                        mt: 2,
                        background:
                          "linear-gradient(90deg, #23293a 40%, #23293a90 100%)",
                        p: 2,
                        borderRadius: 2,
                      }}
                    >
                      <strong>Explanation:</strong>
                      <div>
                        This solution was chosen because it had the highest fitness in the final
                        generation. The fitness improved from{" "}
                        {result.history && result.history[0]} to{" "}
                        {result.history && result.history[result.history.length - 1]} over{" "}
                        {result.history && result.history.length} generations.
                      </div>
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>
          </Fade>
        )}
      </Container>
      {/* Share dialog */}
      <Dialog open={shareDialog} onClose={() => setShareDialog(false)}>
        <DialogTitle>Shareable Link</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Share this link with others to let them view and rerun your problem setup:
          </DialogContentText>
          <Box
            sx={{
              mt: 2,
              p: 1,
              border: "1px solid #333",
              borderRadius: 1,
              background: "#131720",
              fontFamily: "monospace",
              fontSize: 13,
              overflowWrap: "anywhere",
            }}
          >
            {`${window.location.origin}${window.location.pathname}#${encodeURIComponent(
              JSON.stringify({ p: selectedProblem?.id, params })
            )}`}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCopyShareLink} startIcon={<ShareIcon />}>
            Copy Link
          </Button>
          <Button onClick={() => setShareDialog(false)} color="secondary">
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </ThemeProvider>
  );
}

export default App;