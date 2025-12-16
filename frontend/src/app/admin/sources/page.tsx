"use client"

export const dynamic = 'force-dynamic';

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Plus, Search, Trash2, Edit, RefreshCw } from "lucide-react"
import { adminService, Source } from "@/services/adminService"

export default function SourcesPage() {
    const [sources, setSources] = useState<Source[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState("")

    useEffect(() => {
        fetchSources()
    }, [])

    const fetchSources = async () => {
        setLoading(true)
        try {
            const data = await adminService.getSources()
            setSources(data)
        } catch (error) {
            console.error("Failed to fetch sources:", error)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this source?")) return
        try {
            await adminService.deleteSource(id)
            fetchSources()
        } catch (error) {
            console.error("Failed to delete source:", error)
        }
    }

    const filteredSources = sources.filter(s =>
        s.url.toLowerCase().includes(filter.toLowerCase()) ||
        s.type.toLowerCase().includes(filter.toLowerCase())
    )

    return (
        <div className="p-8 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Source Management</h1>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={fetchSources}>
                        <RefreshCw className="mr-2 h-4 w-4" /> Refresh
                    </Button>
                    <Button>
                        <Plus className="mr-2 h-4 w-4" /> Add Source
                    </Button>
                </div>
            </div>

            <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 text-muted-foreground" />
                <Input
                    placeholder="Filter sources..."
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="max-w-sm"
                />
            </div>

            <div className="border rounded-md">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>URL</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Method</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Last Scraped</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {loading ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center py-8">Loading...</TableCell>
                            </TableRow>
                        ) : filteredSources.length === 0 ? (
                            <TableRow>
                                <TableCell colSpan={6} className="text-center py-8">No sources found</TableCell>
                            </TableRow>
                        ) : (
                            filteredSources.map((source) => (
                                <TableRow key={source.id}>
                                    <TableCell className="font-medium truncate max-w-[300px]" title={source.url}>
                                        {source.url}
                                    </TableCell>
                                    <TableCell>
                                        <Badge variant="outline">{source.type}</Badge>
                                    </TableCell>
                                    <TableCell>{source.source_method}</TableCell>
                                    <TableCell>
                                        <Badge variant={source.status === 'active' ? 'default' : 'secondary'}>
                                            {source.status}
                                        </Badge>
                                    </TableCell>
                                    <TableCell>{source.last_scraped_at ? new Date(source.last_scraped_at).toLocaleDateString() : 'Never'}</TableCell>
                                    <TableCell className="text-right space-x-2">
                                        <Button variant="ghost" size="icon">
                                            <Edit className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon" onClick={() => handleDelete(source.id)}>
                                            <Trash2 className="h-4 w-4 text-red-500" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}