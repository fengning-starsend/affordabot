import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || process.env.VITE_API_URL || process.env.RAILWAY_SERVICE_BACKEND_URL || 'http://localhost:8000';

export async function GET(
    request: NextRequest,
    { params }: { params: { taskId: string } }
) {
    const taskId = params.taskId;

    try {
        const response = await fetch(`${BACKEND_URL}/admin/tasks/${taskId}`);

        if (!response.ok) {
            // Pass through the error from backend if possible, or generic
            const error = await response.text();
            return NextResponse.json(
                { error: 'Failed to fetch task status', details: error },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error(`API route error fetching task ${taskId}:`, error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
