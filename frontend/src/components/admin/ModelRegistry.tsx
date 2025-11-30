'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
    Settings,
    Loader2,
    Save,
    Plus,
    GripVertical,
    CheckCircle2,
    XCircle,
    AlertCircle
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface ModelConfig {
    id?: string;
    provider: 'openrouter' | 'zai';
    model_name: string;
    priority: number;
    enabled: boolean;
    use_case: 'generation' | 'review' | 'both';
}

const PROVIDERS = [
    { value: 'openrouter', label: 'OpenRouter' },
    { value: 'zai', label: 'Z.ai' },
];

const USE_CASES = [
    { value: 'generation', label: 'Generation' },
    { value: 'review', label: 'Review' },
    { value: 'both', label: 'Both' },
];

export function ModelRegistry() {
    const [models, setModels] = useState<ModelConfig[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [showAddForm, setShowAddForm] = useState(false);
    const [alert, setAlert] = useState<{ type: 'success' | 'error', message: string } | null>(null);

    // New model form state
    const [newModel, setNewModel] = useState<Partial<ModelConfig>>({
        provider: 'openrouter',
        model_name: '',
        priority: 999,
        enabled: true,
        use_case: 'generation',
    });

    // Load models on mount
    useEffect(() => {
        loadModels();
    }, []);

    const loadModels = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/admin/models');
            if (!response.ok) throw new Error('Failed to load models');
            const data = await response.json();
            setModels(data.sort((a: ModelConfig, b: ModelConfig) => a.priority - b.priority));
        } catch (error) {
            setAlert({ type: 'error', message: 'Failed to load models' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveModels = async () => {
        setIsSaving(true);
        setAlert(null);

        try {
            const response = await fetch('/api/admin/models', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ models }),
            });

            if (!response.ok) throw new Error('Failed to save models');

            setAlert({ type: 'success', message: 'Model configuration saved successfully' });
        } catch (error) {
            setAlert({ type: 'error', message: 'Failed to save model configuration' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleToggleEnabled = (index: number) => {
        const updated = [...models];
        updated[index].enabled = !updated[index].enabled;
        setModels(updated);
    };

    const handlePriorityChange = (index: number, direction: 'up' | 'down') => {
        const updated = [...models];
        const currentPriority = updated[index].priority;

        if (direction === 'up' && index > 0) {
            // Swap with previous
            const prevPriority = updated[index - 1].priority;
            updated[index].priority = prevPriority;
            updated[index - 1].priority = currentPriority;
            updated.sort((a, b) => a.priority - b.priority);
        } else if (direction === 'down' && index < updated.length - 1) {
            // Swap with next
            const nextPriority = updated[index + 1].priority;
            updated[index].priority = nextPriority;
            updated[index + 1].priority = currentPriority;
            updated.sort((a, b) => a.priority - b.priority);
        }

        setModels(updated);
    };

    const handleAddModel = () => {
        if (!newModel.model_name) {
            setAlert({ type: 'error', message: 'Model name is required' });
            return;
        }

        const maxPriority = Math.max(...models.map(m => m.priority), 0);
        const modelToAdd: ModelConfig = {
            provider: newModel.provider as 'openrouter' | 'zai',
            model_name: newModel.model_name,
            priority: maxPriority + 1,
            enabled: newModel.enabled ?? true,
            use_case: newModel.use_case as 'generation' | 'review' | 'both',
        };

        setModels([...models, modelToAdd]);
        setShowAddForm(false);
        setNewModel({
            provider: 'openrouter',
            model_name: '',
            priority: 999,
            enabled: true,
            use_case: 'generation',
        });
        setAlert({ type: 'success', message: 'Model added. Click Save to persist changes.' });
    };

    const getUseCaseBadge = (useCase: string) => {
        const variants: Record<string, string> = {
            generation: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
            review: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
            both: 'bg-green-500/20 text-green-300 border-green-500/30',
        };

        return (
            <Badge className={variants[useCase] || ''}>
                {useCase}
            </Badge>
        );
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

            {/* Model List */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="text-white">Model Configuration</CardTitle>
                            <CardDescription className="text-slate-300">
                                Manage LLM models and their priority order
                            </CardDescription>
                        </div>
                        <div className="flex gap-2">
                            <Button
                                onClick={() => setShowAddForm(!showAddForm)}
                                variant="outline"
                                className="bg-white/5 border-white/20 text-white hover:bg-white/10"
                            >
                                <Plus className="w-4 h-4 mr-2" />
                                Add Model
                            </Button>
                            <Button
                                onClick={handleSaveModels}
                                disabled={isSaving}
                                className="bg-purple-600 hover:bg-purple-700"
                            >
                                {isSaving ? (
                                    <>
                                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4 mr-2" />
                                        Save Changes
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {/* Add Model Form */}
                    {showAddForm && (
                        <div className="mb-6 p-4 rounded-lg bg-white/5 border border-white/20 space-y-4">
                            <h3 className="text-white font-medium">Add New Model</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label className="text-white">Provider</Label>
                                    <Select
                                        value={newModel.provider}
                                        onValueChange={(value) => setNewModel({ ...newModel, provider: value as any })}
                                    >
                                        <SelectTrigger className="bg-white/5 border-white/20 text-white">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {PROVIDERS.map(p => (
                                                <SelectItem key={p.value} value={p.value}>
                                                    {p.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-white">Model Name</Label>
                                    <Input
                                        placeholder="e.g., x-ai/grok-beta"
                                        value={newModel.model_name}
                                        onChange={(e) => setNewModel({ ...newModel, model_name: e.target.value })}
                                        className="bg-white/5 border-white/20 text-white placeholder:text-slate-400"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label className="text-white">Use Case</Label>
                                    <Select
                                        value={newModel.use_case}
                                        onValueChange={(value) => setNewModel({ ...newModel, use_case: value as any })}
                                    >
                                        <SelectTrigger className="bg-white/5 border-white/20 text-white">
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {USE_CASES.map(u => (
                                                <SelectItem key={u.value} value={u.value}>
                                                    {u.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="flex items-end">
                                    <Button onClick={handleAddModel} className="w-full bg-green-600 hover:bg-green-700">
                                        <Plus className="w-4 h-4 mr-2" />
                                        Add Model
                                    </Button>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Models Table */}
                    {isLoading ? (
                        <div className="text-center py-8">
                            <Loader2 className="w-8 h-8 mx-auto text-purple-400 animate-spin" />
                            <p className="text-slate-400 mt-2">Loading models...</p>
                        </div>
                    ) : models.length === 0 ? (
                        <div className="text-center py-8 text-slate-400">
                            <Settings className="w-12 h-12 mx-auto mb-3 opacity-50" />
                            <p>No models configured</p>
                            <p className="text-sm mt-1">Add a model to get started</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow className="border-white/10 hover:bg-white/5">
                                    <TableHead className="text-slate-300 w-12">Priority</TableHead>
                                    <TableHead className="text-slate-300">Provider</TableHead>
                                    <TableHead className="text-slate-300">Model Name</TableHead>
                                    <TableHead className="text-slate-300">Use Case</TableHead>
                                    <TableHead className="text-slate-300">Status</TableHead>
                                    <TableHead className="text-slate-300 w-24">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {models.map((model, index) => (
                                    <TableRow key={index} className="border-white/10 hover:bg-white/5">
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                <div className="flex flex-col">
                                                    <button
                                                        onClick={() => handlePriorityChange(index, 'up')}
                                                        disabled={index === 0}
                                                        className="text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                                    >
                                                        ▲
                                                    </button>
                                                    <button
                                                        onClick={() => handlePriorityChange(index, 'down')}
                                                        disabled={index === models.length - 1}
                                                        className="text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                                    >
                                                        ▼
                                                    </button>
                                                </div>
                                                <span className="text-white font-mono text-sm">{model.priority}</span>
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-white font-medium capitalize">
                                            {model.provider}
                                        </TableCell>
                                        <TableCell className="text-slate-300 font-mono text-sm">
                                            {model.model_name}
                                        </TableCell>
                                        <TableCell>
                                            {getUseCaseBadge(model.use_case)}
                                        </TableCell>
                                        <TableCell>
                                            <div className="flex items-center gap-2">
                                                {model.enabled ? (
                                                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                                                ) : (
                                                    <XCircle className="w-4 h-4 text-red-400" />
                                                )}
                                                <span className={model.enabled ? 'text-green-300' : 'text-red-300'}>
                                                    {model.enabled ? 'Enabled' : 'Disabled'}
                                                </span>
                                            </div>
                                        </TableCell>
                                        <TableCell>
                                            <Switch
                                                checked={model.enabled}
                                                onCheckedChange={() => handleToggleEnabled(index)}
                                            />
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Model Health (Placeholder) */}
            <Card className="bg-white/10 backdrop-blur-md border-white/20">
                <CardHeader>
                    <CardTitle className="text-white">Model Health Status</CardTitle>
                    <CardDescription className="text-slate-300">
                        Real-time health monitoring for configured models
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8 text-slate-400">
                        <Settings className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>Health monitoring coming soon</p>
                        <p className="text-sm mt-1">Will show latency, success rate, and availability</p>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
