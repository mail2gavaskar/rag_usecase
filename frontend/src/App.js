import React, { useState } from 'react';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  CircularProgress,
  Snackbar,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://localhost:8000';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const onDrop = async (acceptedFiles) => {
    const formData = new FormData();
    formData.append('file', acceptedFiles[0]);

    try {
      setLoading(true);
      await axios.post(`${API_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSnackbar({
        open: true,
        message: 'Document uploaded successfully',
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error uploading document',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    }
  });

  const handleQuery = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/query`, {
        text: query,
        k: 5
      });
      setResponse(response.data);
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Error processing query',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const TokenUsageTable = ({ tokenUsage }) => (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Operation</TableCell>
            <TableCell align="right">Input Tokens</TableCell>
            <TableCell align="right">Output Tokens</TableCell>
            <TableCell align="right">Total Tokens</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Summary</TableCell>
            <TableCell align="right">{tokenUsage.summary.input_tokens}</TableCell>
            <TableCell align="right">{tokenUsage.summary.output_tokens}</TableCell>
            <TableCell align="right">{tokenUsage.summary.total_tokens}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Recommendations</TableCell>
            <TableCell align="right">{tokenUsage.recommendations.input_tokens}</TableCell>
            <TableCell align="right">{tokenUsage.recommendations.output_tokens}</TableCell>
            <TableCell align="right">{tokenUsage.recommendations.total_tokens}</TableCell>
          </TableRow>
          <TableRow>
            <TableCell><strong>Total</strong></TableCell>
            <TableCell align="right"><strong>{tokenUsage.total.input_tokens}</strong></TableCell>
            <TableCell align="right"><strong>{tokenUsage.total.output_tokens}</strong></TableCell>
            <TableCell align="right"><strong>{tokenUsage.total.total_tokens}</strong></TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </TableContainer>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          Bank Document Analysis System
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper
              {...getRootProps()}
              sx={{
                p: 3,
                textAlign: 'center',
                backgroundColor: isDragActive ? '#e3f2fd' : '#f5f5f5',
                cursor: 'pointer'
              }}
            >
              <input {...getInputProps()} />
              <Typography variant="h6">
                {isDragActive
                  ? 'Drop the document here'
                  : 'Drag and drop a document here, or click to select'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Supported formats: PDF, DOC, DOCX, TXT
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <TextField
                fullWidth
                multiline
                rows={4}
                variant="outlined"
                label="Enter your query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button
                variant="contained"
                color="primary"
                onClick={handleQuery}
                disabled={loading}
                fullWidth
              >
                {loading ? <CircularProgress size={24} /> : 'Submit Query'}
              </Button>
            </Paper>
          </Grid>

          {response && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Summary
                </Typography>
                <ReactMarkdown>{response.summary}</ReactMarkdown>

                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Recommendations
                </Typography>
                <ReactMarkdown>{response.recommendations[0]}</ReactMarkdown>

                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Sources
                </Typography>
                <ul>
                  {response.sources.map((source, index) => (
                    <li key={index}>{source}</li>
                  ))}
                </ul>

                <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                  Token Usage
                </Typography>
                <TokenUsageTable tokenUsage={response.token_usage} />
              </Paper>
            </Grid>
          )}
        </Grid>
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
}

export default App; 