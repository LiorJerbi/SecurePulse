function StatsBar({ alerts, totalLogs }) {
    const critical = alerts.filter(a => a.severity === 'CRITICAL').length
    const high = alerts.filter(a => a.severity === 'HIGH').length
    const medium = alerts.filter(a => a.severity === 'MEDIUM').length

    const stats = [
        { label: 'Total Logs', value: totalLogs, color: '#64748b' },
        { label: 'Total Alerts', value: alerts.length, color: '#f59e0b' },
        { label: 'Critical', value: critical, color: '#ef4444' },
        { label: 'High', value: high, color: '#f97316' },
        { label: 'Medium', value: medium, color: '#eab308' },
    ]

    return (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {stats.map(stat => (
                <div key={stat.label} style={{
                    background: '#1e293b',
                    border: `1px solid ${stat.color}40`,
                    borderRadius: 8,
                    padding: '16px 24px',
                    minWidth: 120,
                    flex: 1,
                }}>
                    <div style={{ fontSize: 28, fontWeight: 700, color: stat.color }}>
                        {stat.value}
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
                        {stat.label}
                    </div>
                </div>
            ))}
        </div>
    )
}

export default StatsBar