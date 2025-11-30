'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PlayCircle, Loader2, CheckCircle2, XCircle, Zap, FileSearch, FileText, CheckSquare } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

const JURISDICTIONS = [
    { value: 'san_jose', label: 'San Jose' },
    { value: 'saratoga', label: 'Saratoga' },
    { value: 'santa_clara_county', label: 'Santa Clara County' },
    { value: 'california_state', label: 'California State' },
];

const ANALYSIS_STEPS = [
    { value: 'research', label: 'Research', icon: FileSearch, description: 'Gather background information' },
    { value: 'generate', label: 'Generate', icon: FileText, description: 'Create impact analysis' },
    { value: 'review', label: 'Review', icon: CheckSquare, description: 'Quality check and validation' },
];

interface AnalysisTask {
    task_id: string;
    jurisdiction: string;
    bill_id: string;
    step: string;
    status: 'started' | 'completed' | 'failed';
    timestamp: string;
}

interface AnalysisHistory {
    id: string;
    jurisdiction: string;
    bill_id: string;
    step: string;
    model_used: string;
    timestamp: string;
    status: 'success' | 'failed';
    result?: any;
    error?: string;
}

export function AnalysisLab() {
    const [jurisdiction, setJurisdiction] = useState<string>('');
    const [billId, setBillId] = useState<string>('');
    const [step, setStep] = useState<string>('');
    const [modelOverride, setModelOverride] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);
    const [activeTasks, setActiveTasks] = useState<AnalysisTask[]>([]);
    const [history, setHistory] = useState<AnalysisHistory[]>([]);
    const [alert, setAlert] = useState<{ type: 'success' | 'error', message: string } | null>(null);

    const handleRunAnalysis = async () => {
        if (!jurisdiction || !billId || !step) {
            setAlert({ type: 'error', message: 'Please fill in all required fields' });
            return;
        }

        setIsLoading(true);
        setAlert(null);

        try {
            const response = await fetch('/api/admin/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jurisdiction,
                    bill_id: billId,
                    step,
                    model_override: modelOverride || null,
                }),
            });

            if (!response.ok) throw new Error('Failed to run analysis');

            const data = await response.json();

            // Add to active tasks
            setActiveTasks(prev => [
                {
                    task_id: data.task_id,
                    jurisdiction,
                    bill_id: billId,
                    step,
                    status: 'started',
                    timestamp: new Date().toISOString(),
                },
                ...prev,
            ]);

            setAlert({ type: 'success', message: `Running ${step} analysis for ${billId}...` });

            // Reset form
            setBillId('');
            setStep('');
            setModelOverride('');
        } catch (error) {
            setAlert({ type: 'error', message: 'Failed to run analysis' });
        } finally {
            setIsLoading(false);
        }
    };

    const getStepIcon = (stepName: string) => {
        const stepConfig = ANALYSIS_STEPS.find(s => s.value === stepName);
        if (!stepConfig) return Zap;
        return stepConfig.icon;
    };

    const getStatusBadge = (status: string) => {
        const variants: Record<string, string> = {
            started: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            completed: 'bg-green-500/20 text-green-300 border-green-500/30',
            success: 'bg-green-500/20 text-green-300 border-green-500/30',
            failed: 'bg-red-500/20 text-red-300 border-red-500/30',
        };

        return (
            <Badge className={variants[status] || ''}>
                {status}
            </Badge>
        );
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'started':
                return <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />;
            case 'completed':
            case 'success':
                return <CheckCircle2 className="w-4 h-4 text-green-400" />;
            case 'failed':
                return <XCircle className="w-4 h-4 text-red-400" />;
            default:
                return null;
        }
    };

    return (
        <div className="space-y-6">
            {/* Alert */}
            {alert && (
                <Alert className={alert.type === 'error' ? 'bg-red-500/20 border-red-500/30' : 'bg-green-500/20 border-green-500/30'}>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-white">
                        {alert.message}
                    </AlertDescription>
                </Alert>
            )}

            {/* Run Analysis */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                    <CardTitle className="text-white">Run Analysis Pipeline</CardTitle>
                    <CardDescription className="text-slate-300">
                        Execute research, generation, or review steps for a specific bill
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Bill Selection */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label className="text-white">Jurisdiction</Label>
                            <Select value={jurisdiction} onValueChange={setJurisdiction}>
                                <SelectTrigger className="bg-white/5 border-white/20 text-white">
                                    <SelectValue placeholder="Select jurisdiction" />
                                </SelectTrigger>
                                <SelectContent>
                                    {JURISDICTIONS.map(j => (
                                        <SelectItem key={j.value} value={j.value}>
                                            {j.label}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label className="text-white">Bill ID</Label>
                            <Input
                                placeholder="e.g., SB-123"
                                value={billId}
                                onChange={(e) => setBillId(e.target.value)}
                                className="bg-white/5 border-white/20 text-white placeholder:text-slate-400"
                            />
                        </div>
                    </div>

                    {/* Analysis Step Selection */}
                    <div className="space-y-2">
                        <Label className="text-white">Analysis Step</Label>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {ANALYSIS_STEPS.map(s => {
                                const Icon = s.icon;
                                return (
                                    <button
                                        key={s.value}
                                        onClick={() => setStep(s.value)}
                                        className={`p-4 rounded-lg border-2 transition-all ${step === s.value
                                                ? 'bg-purple-500/20 border-purple-500'
                                                : 'bg-white/5 border-white/20 hover:border-white/40'
                                            }`}
                                    >
                                        <div className="flex items-center gap-3 mb-2">
                                            <Icon className={`w-5 h-5 ${step === s.value ? 'text-purple-300' : 'text-slate-300'}`} />
                                            <span className={`font-medium ${step === s.value ? 'text-purple-300' : 'text-white'}`}>
                                                {s.label}
                                            </span>
                                        </div>
                                        <p className="text-sm text-slate-400 text-left">{s.description}</p>
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    {/* Model Override (Optional) */}
                    <div className="space-y-2">
                        <Label className="text-white">Model Override (Optional)</Label>
                        <Input
                            placeholder="e.g., openrouter/x-ai/grok-beta"
                            value={modelOverride}
                            onChange={(e) => setModelOverride(e.target.value)}
                            className="bg-white/5 border-white/20 text-white placeholder:text-slate-400"
                        />
                        <p className="text-xs text-slate-400">Leave empty to use default model for this step</p>
                    </div>

                    {/* Run Button */}
                    <Button
                        onClick={handleRunAnalysis}
                        disabled={isLoading || !jurisdiction || !billId || !step}
                        className="w-full bg-purple-600 hover:bg-purple-700"
                    >
                        {isLoading ? (
                            <>
                                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                Running...
                            </>
                        ) : (
                            <>
                                <PlayCircle className="w-4 h-4 mr-2" />
                                Run Analysis
                            </>
                        )}
                    </Button>
                </CardContent>
            </Card>

            {/* Active Tasks */}
            {activeTasks.length > 0 && (
                <Card className="bg-white/10 backdrop-blur-md border-white/20">
                    <CardHeader>
                        <CardTitle className="text-white">Active Analysis Tasks</CardTitle>
                        <CardDescription className="text-slate-300">
                            Currently running analysis operations
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/10 hover:bg-white/5">
                                    <TableHead className="text-slate-300">Status</TableHead>
                                    <TableHead className="text-slate-300">Step</TableHead>
                                    <TableHead className="text-slate-300">Bill ID</TableHead>
                                    <TableHead className="text-slate-300">Jurisdiction</TableHead>
                                    <TableHead className="text-slate-300">Started</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {activeTasks.map(task => {
                                    const Icon = getStepIcon(task.step);
                                    return (
                                        <TableRow key={task.task_id} className="border-white/10 hover:bg-white/5">
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    {getStatusIcon(task.status)}
                                                    {getStatusBadge(task.status)}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <Icon className="w-4 h-4 text-slate-300" />
                                                    <span className="text-white font-medium capitalize">{task.step}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-white font-mono">{task.bill_id}</TableCell>
                                            <TableCell className="text-slate-300">{task.jurisdiction}</TableCell>
                                            <TableCell className="text-slate-300">
                                                {new Date(task.timestamp).toLocaleTimeString()}
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}

            {/* Analysis History */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                    <CardTitle className="text-white">Analysis History</CardTitle>
                    <CardDescription className="text-slate-300">
                        Recent analysis pipeline executions
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {history.length === 0 ? (
                        <div className="text-center py-8 text-slate-400">
                            <Zap className="w-12 h-12 mx-auto mb-3 opacity-50" />
                            <p>No analysis history yet</p>
                            <p className="text-sm mt-1">Run an analysis to see results here</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/10 hover:bg-white/5">
                                    <TableHead className="text-slate-300">Status</TableHead>
                                    <TableHead className="text-slate-300">Step</TableHead>
                                    <TableHead className="text-slate-300">Bill ID</TableHead>
                                    <TableHead className="text-slate-300">Model</TableHead>
                                    <TableHead className="text-slate-300">Timestamp</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {history.map(item => {
                                    const Icon = getStepIcon(item.step);
                                    return (
                                        <TableRow key={item.id} className="border-white/10 hover:bg-white/5">
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    {getStatusIcon(item.status)}
                                                    {getStatusBadge(item.status)}
                                                </div>
                                            </TableCell>
                                            <TableCell>
                                                <div className="flex items-center gap-2">
                                                    <Icon className="w-4 h-4 text-slate-300" />
                                                    <span className="text-white font-medium capitalize">{item.step}</span>
                                                </div>
                                            </TableCell>
                                            <TableCell className="text-white font-mono">{item.bill_id}</TableCell>
                                            <TableCell className="text-slate-300 text-sm">{item.model_used}</TableCell>
                                            <TableCell className="text-slate-300">
                                                {new Date(item.timestamp).toLocaleString()}
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
