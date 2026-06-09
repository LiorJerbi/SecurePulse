const SEVERITY_COLORS = {
    CRITICAL: '#ef4444',
    HIGH: '#f97316',
    MEDIUM: '#eab308',
    LOW: '#22c55e',
}

function AlertsFeed({ alerts, onSelectAlert, selectedAlert }) {
    if (alerts.length === 0) {
        return (
            <div style={{ color: '#64748b', padding: 20, textAlign: 'center' }}>
                No alerts. Run analysis first.
            </div>
        )
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {alerts.map(alert => (
                <div
                    key={alert.id}
                    onClick={() => onSelectAlert(alert)}
                    style={{
                        background: selectedAlert?.id === alert.id ? '#1e3a5f' : '#1e293b',
                        border: `1px solid ${SEVERITY_COLORS[alert.severity]}40`,
                        borderLeft: `3px solid ${SEVERITY_COLORS[alert.severity]}`,
                        borderRadius: 6,
                        padding: '12px 16px',
                        cursor: 'pointer',
                        transition: 'background 0.15s',
                    }}
                >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontWeight: 600, color: '#e2e8f0', fontSize: 14 }}>
                            {alert.alert_type.replace(/_/g, ' ')}
                        </span>
                        <span style={{
                            fontSize: 11,
                            color: SEVERITY_COLORS[alert.severity],
                            border: `1px solid ${SEVERITY_COLORS[alert.severity]}`,
                            padding: '2px 8px',
                            borderRadius: 4,
                        }}>
                            {alert.severity}
                        </span>
                    </div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 4 }}>
                        {alert.source_ip} · {new Date(alert.created_at).toLocaleTimeString()}
                    </div>
                    <div style={{ fontSize: 12, color: '#64748b', marginTop: 4 }}>
                        {alert.description}
                    </div>
                </div>
            ))}
        </div>
    )
}

export default AlertsFeed