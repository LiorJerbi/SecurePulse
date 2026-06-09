import { useState } from 'react'
import { fetchLogs } from '../api'

function LogViewer() {
    const [logs, setLogs] = useState(null)
    const [page, setPage] = useState(1)
    const [filterIp, setFilterIp] = useState('')
    const [loading, setLoading] = useState(false)

    const loadLogs = async (newPage = 1, ip = filterIp) => {
        setLoading(true)
        try {
            const filters = ip ? { source_ip: ip } : {}
            const data = await fetchLogs(newPage, 10, filters)
            setLogs(data)
            setPage(newPage)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                <input
                    value={filterIp}
                    onChange={e => setFilterIp(e.target.value)}
                    placeholder="Filter by IP..."
                    style={{
                        background: '#0f172a',
                        border: '1px solid #334155',
                        borderRadius: 6,
                        padding: '6px 12px',
                        color: '#e2e8f0',
                        fontSize: 13,
                        flex: 1,
                    }}
                />
                <button
                    onClick={() => loadLogs(1)}
                    style={{
                        background: '#1e40af',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 6,
                        padding: '6px 16px',
                        cursor: 'pointer',
                        fontSize: 13,
                    }}
                >
                    {logs ? 'Refresh' : 'Load Logs'}
                </button>
            </div>

            {loading && <div style={{ color: '#64748b', fontSize: 13 }}>Loading...</div>}

            {logs && (
                <>
                    <div style={{ fontSize: 11, color: '#64748b', marginBottom: 8 }}>
                        {logs.total} total entries · page {logs.page}
                    </div>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid #334155' }}>
                                    {['Time', 'IP', 'Type', 'Event'].map(h => (
                                        <th key={h} style={{ padding: '6px 8px', textAlign: 'left', color: '#64748b' }}>
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {logs.results.map(log => (
                                    <tr key={log.id} style={{ borderBottom: '1px solid #1e293b' }}>
                                        <td style={{ padding: '6px 8px', color: '#64748b' }}>
                                            {new Date(log.timestamp).toLocaleTimeString()}
                                        </td>
                                        <td style={{ padding: '6px 8px', color: '#94a3b8' }}>
                                            {log.source_ip}
                                        </td>
                                        <td style={{ padding: '6px 8px' }}>
                                            <span style={{
                                                color: log.log_type === 'apache' ? '#60a5fa' : '#a78bfa',
                                                fontSize: 11,
                                            }}>
                                                {log.log_type.toUpperCase()}
                                            </span>
                                        </td>
                                        <td style={{ padding: '6px 8px', color: '#64748b', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {log.event || `${log.method} ${log.path} ${log.status_code}`}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                        <button
                            onClick={() => loadLogs(page - 1)}
                            disabled={page <= 1}
                            style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: 4, padding: '4px 12px', cursor: page <= 1 ? 'not-allowed' : 'pointer' }}
                        >
                            ← Prev
                        </button>
                        <button
                            onClick={() => loadLogs(page + 1)}
                            disabled={logs.results.length < 10}
                            style={{ background: '#1e293b', color: '#94a3b8', border: '1px solid #334155', borderRadius: 4, padding: '4px 12px', cursor: 'pointer' }}
                        >
                            Next →
                        </button>
                    </div>
                </>
            )}
        </div>
    )
}

export default LogViewer