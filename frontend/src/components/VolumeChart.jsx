import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

function VolumeChart({ logs }) {
    if (!logs || logs.length === 0) return null

    const counts = {}
    logs.forEach(log => {
        const hour = new Date(log.timestamp).getHours()
        const label = `${String(hour).padStart(2, '0')}:00`
        counts[label] = (counts[label] || 0) + 1
    })

    const data = Object.entries(counts)
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([hour, count]) => ({ hour, count }))

    return (
        <div style={{ background: '#1e293b', borderRadius: 10, padding: 16, marginBottom: 20 }}>
            <div style={{ fontSize: 13, color: '#64748b', marginBottom: 16, textTransform: 'uppercase', letterSpacing: 1 }}>
                Log Volume by Hour
            </div>
            <ResponsiveContainer width="100%" height={160}>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e3a5f" />
                    <XAxis dataKey="hour" tick={{ fill: '#64748b', fontSize: 11 }} />
                    <YAxis tick={{ fill: '#64748b', fontSize: 11 }} />
                    <Tooltip
                        contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 6 }}
                        labelStyle={{ color: '#94a3b8' }}
                        itemStyle={{ color: '#60a5fa' }}
                    />
                    <Line type="monotone" dataKey="count" stroke="#2563eb" strokeWidth={2} dot={{ fill: '#2563eb', r: 3 }} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    )
}

export default VolumeChart