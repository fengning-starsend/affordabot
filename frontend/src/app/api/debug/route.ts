import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
    const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

    try {
        const response = await fetch(`${BACKEND_URL}/admin/models`, {
            cache: 'no-store'
        });

        const data = await response.json().catch(e => ({ error: 'Failed to parse JSON', raw: e.message }));

        return NextResponse.json({
            status: 'success',
            backend_url: BACKEND_URL,
            response_status: response.status,
            data: data
        });
    } catch (error) {
        return NextResponse.json({
            status: 'error',
            backend_url: BACKEND_URL,
            error: error instanceof Error ? error.message : String(error),
            stack: error instanceof Error ? error.stack : undefined
        }, { status: 500 });
    }
}
