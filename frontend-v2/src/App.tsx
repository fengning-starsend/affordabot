import { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Box, AppBar, Toolbar, Typography, Container, Tabs, Tab } from '@mui/material'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import GlassBoxViewer from './components/GlassBoxViewer'
import LegislationList from './components/LegislationList'

const darkTheme = createTheme({
    palette: {
        mode: 'dark',
    },
});

const queryClient = new QueryClient();

interface TabPanelProps {
    children?: React.ReactNode;
    index: number;
    value: number;
}

function CustomTabPanel(props: TabPanelProps) {
    const { children, value, index, ...other } = props;

    return (
        <div
            role="tabpanel"
            hidden={value !== index}
            id={`simple-tabpanel-${index}`}
            aria-labelledby={`simple-tab-${index}`}
            {...other}
            style={{ height: '100%' }}
        >
            {value === index && (
                <Box sx={{ p: 3, height: '100%' }}>
                    {children}
                </Box>
            )}
        </div>
    );
}

function App() {
    const [value, setValue] = useState(0);

    const handleChange = (_event: React.SyntheticEvent, newValue: number) => {
        setValue(newValue);
    };

    return (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={darkTheme}>
                <CssBaseline />
                <Box sx={{ flexGrow: 1, height: '100vh', display: 'flex', flexDirection: 'column' }}>
                    <AppBar position="static">
                        <Toolbar>
                            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                                Affordabot V2 Prototype
                            </Typography>
                            <Tabs value={value} onChange={handleChange} textColor="inherit">
                                <Tab label="Legislation Analysis" />
                                <Tab label="Agent GlassBox" />
                            </Tabs>
                        </Toolbar>
                    </AppBar>
                    <Container maxWidth="xl" sx={{ mt: 2, flex: 1, pb: 4, height: 'calc(100vh - 80px)' }}>
                        <CustomTabPanel value={value} index={0}>
                            {/* Default to San Jose for prototype */}
                            <LegislationList jurisdiction="sanjose" />
                        </CustomTabPanel>
                        <CustomTabPanel value={value} index={1}>
                            <GlassBoxViewer />
                        </CustomTabPanel>
                    </Container>
                </Box>
            </ThemeProvider>
        </QueryClientProvider>
    )
}

export default App
