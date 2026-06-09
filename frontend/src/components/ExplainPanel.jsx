import { useState } from 'react'
import { explainAlert } from '../api'

function ExplainPanel({ alert }) {
    const [explanation, setExplanation] = useState(alert?.ai_explanation || null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const handleExplain = async () => {
        setLoading(true)
        setError(null)
        try {
            const updated = await explainAlert(alert.id)
            setExplanation(updated.ai_explanation)
        } catch (e) {
            setError('Failed to get explanation. Try again.')
        } finally {
            setLoading(false)
        }
    }

    if (!alert) {
        return (
            <div style={{ color: '#64748b', padding: 20, textAlign: 'center' }}>
                Select an alert to see details
            </div>
        )
    }

    return (
        <div style={{ padding: 16 }}>
            <div style={{ fontSize: 16, fontWeight: 700, color: '#e2e8f0', marginBottom: 8 }}>
                {alert.alert_type.replace(/_/g, ' ')}
            </div>
            <div style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>
                {alert.source_ip} · {alert.severity}
            </div>

            {explanation ? (
                <div style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.8, whiteSpace: 'pre-line' }}>
                    {explanation}
                </div>
            ) : (
                <button
                    onClick={handleExplain}
                    disabled={loading}
                    style={{
                        background: loading ? '#334155' : '#2563eb',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 6,
                        padding: '8px 16px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: 13,
                    }}
                >
                    {loading ? 'Analyzing...' : '✨ Explain with AI'}
                </button>
            )}

            {error && (
                <div style={{ color: '#ef4444', fontSize: 12, marginTop: 8 }}>
                    {error}
                </div>
            )}
        </div>
    )
}

export default ExplainPanel