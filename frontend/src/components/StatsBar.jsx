function StatsBar({ alerts, totalLogs }) {
    const critical = alerts.filter(a => a.severity === 'CRITICAL').length
    const high = alerts.filter(a => a.severity === 'HIGH').length
    const medium = alerts.filter(a => a.severity === 'MEDIUM').length

    const stats = [
        { label: 'Total Logs', value: totalLogs, color: '#60a5fa', icon: '📋', bg: '#1e3a5f' },
        { label: 'Total Alerts', value: alerts.length, color: '#f59e0b', icon: '🔔', bg: '#2d2006' },
        { label: 'Critical', value: critical, color: '#ef4444', icon: '🔴', bg: '#2d0a0a' },
        { label: 'High', value: high, color: '#f97316', icon: '🟠', bg: '#2d1506' },
        { label: 'Medium', value: medium, color: '#eab308', icon: '🟡', bg: '#2d2506' },
    ]

    return (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
            {stats.map(stat => (
                <div key={stat.label} style={{
                    background: stat.bg,
                    border: `1px solid ${stat.color}25`,
                    borderRadius: 10,
                    padding: '16px 20px',
                    flex: 1,
                    minWidth: 110,
                    transition: 'transform 0.15s, box-shadow 0.15s',
                    cursor: 'default',
                }}
                    onMouseEnter={e => {
                        e.currentTarget.style.transform = 'translateY(-2px)'
                        e.currentTarget.style.boxShadow = `0 4px 20px ${stat.color}20`
                    }}
                    onMouseLeave={e => {
                        e.currentTarget.style.transform = 'translateY(0)'
                        e.currentTarget.style.boxShadow = 'none'
                    }}
                >
                    <div style={{ fontSize: 24, fontWeight: 700, color: stat.color, fontVariantNumeric: 'tabular-nums' }}>
                        {stat.value}
                    </div>
                    <div style={{ fontSize: 11, color: '#64748b', marginTop: 4, fontWeight: 500, letterSpacing: 0.3 }}>
                        {stat.label.toUpperCase()}
                    </div>
                </div>
            ))}
        </div>
    )
}

export default StatsBar