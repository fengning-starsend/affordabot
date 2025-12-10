'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { adminService, JurisdictionDashboardStats } from '@/services/adminService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Activity, Clock, FileText, AlertTriangle, PlayCircle, ShieldCheck } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export default function JurisdictionDashboard() {
    const params = useParams();
    const id = params.id as string;
    const [stats, setStats] = useState<JurisdictionDashboardStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [taskStatus, setTaskStatus] = useState<string | null>(null);
    const { toast } = useToast();

    const loadStats = () => {
        setLoading(true);
        adminService.getJurisdictionDashboard(id)
            .then(setStats)
            .catch((err) => {
                console.error(err);
                toast({
                    title: "Error",
                    description: "Failed to load dashboard stats",
                    variant: "destructive"
                });
            })
            .finally(() => setLoading(false));
    };

    useEffect(() => {
        if (id) loadStats();
    }, [id]);

    const handleScrape = async (force: boolean) => {
        if (!stats) return;
        try {
            setTaskStatus("Starting scrape...");
            const task = await adminService.triggerScrape(stats.jurisdiction, force);
            setTaskStatus(`Scrape started: ${task.task_id}`);
            toast({
                title: "Scrape Triggered",
                description: `Task ID: ${task.task_id}`
            });
            // Polling could be added here
        } catch (err) {
            console.error(err);
            toast({
                title: "Error",
                description: "Failed to trigger scrape",
                variant: "destructive"
            });
            setTaskStatus("Failed to start scrape");
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
            </div>
        );
    }

    if (!stats) {
        return (
            <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription>Could not load jurisdiction details.</AlertDescription>
            </Alert>
        );
    }

    return (
        <div className="space-y-8 p-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl font-bold text-gray-900">{stats.jurisdiction}</h1>
                    <div className="flex items-center gap-3 mt-2">
                        <Badge variant={stats.pipeline_status === 'healthy' ? 'default' : 'destructive'} className="text-sm px-3 py-1">
                            {stats.pipeline_status === 'healthy' ? (
                                <ShieldCheck className="w-4 h-4 mr-1 inline" />
                            ) : (
                                <AlertTriangle className="w-4 h-4 mr-1 inline" />
                            )}
                            {stats.pipeline_status.toUpperCase()}
                        </Badge>
                        <span className="text-sm text-gray-500 flex items-center">
                            <Clock className="w-4 h-4 mr-1" />
                            Last Scrape: {stats.last_scrape ? new Date(stats.last_scrape).toLocaleString() : 'Never'}
                        </span>
                    </div>
                </div>
                <div className="flex gap-3">
                    <Button variant="outline" onClick={() => loadStats()}>
                        Refresh
                    </Button>
                    <Button onClick={() => handleScrape(false)}>
                        <PlayCircle className="w-4 h-4 mr-2" />
                        Run Scraper
                    </Button>
                    <Button variant="secondary" onClick={() => handleScrape(true)}>
                        Force Rescrape
                    </Button>
                </div>
            </div>

            {/* Task Status Feedback */}
            {taskStatus && (
                <Alert>
                    <Activity className="h-4 w-4" />
                    <AlertTitle>Task Status</AlertTitle>
                    <AlertDescription>{taskStatus}</AlertDescription>
                </Alert>
            )}

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Raw Scrapes</CardTitle>
                        <FileText className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_raw_scrapes}</div>
                        <p className="text-xs text-muted-foreground">
                            Items collected from sources
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Processed Content</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.processed_scrapes}</div>
                        <p className="text-xs text-muted-foreground">
                            Items successfully processed
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Bills Analyzed</CardTitle>
                        <ShieldCheck className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_bills}</div>
                        <p className="text-xs text-muted-foreground">
                            Legislative items generated
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Active Alerts */}
            {stats.active_alerts.length > 0 && (
                <Card className="border-red-200 bg-red-50">
                    <CardHeader>
                        <CardTitle className="text-red-800 flex items-center">
                            <AlertTriangle className="w-5 h-5 mr-2" />
                            Active Alerts
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="list-disc pl-5 space-y-1 text-red-700">
                            {stats.active_alerts.map((alert, i) => (
                                <li key={i}>{alert}</li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}
