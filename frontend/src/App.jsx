import { useState, useEffect } from 'react'
import { fetchAlerts, analyzeAndFetch, fetchLogs } from './api'
import StatsBar from './components/StatsBar'
import AlertsFeed from './components/AlertsFeed'
import ExplainPanel from './components/ExplainPanel'
import LogViewer from './components/LogViewer'
import VolumeChart from './components/VolumeChart'

export default function App() {
    const [alerts, setAlerts] = useState([])
    const [selectedAlert, setSelectedAlert] = useState(null)
    const [totalLogs, setTotalLogs] = useState(0)
    const [analyzing, setAnalyzing] = useState(false)
    const [activeTab, setActiveTab] = useState('alerts')
    const [allLogs, setAllLogs] = useState([])

    useEffect(() => {
        fetchAlerts().then(setAlerts).catch(() => {})
        fetchLogs(1, 100).then(data => {
          setTotalLogs(data.total)
          setAllLogs(data.results)
        }).catch(() => {})
    }, [])

    const handleAnalyze = async () => {
        setAnalyzing(true)
        try {
            const fresh = await analyzeAndFetch()
            setAlerts(fresh)
            setSelectedAlert(null)
        } finally {
            setAnalyzing(false)
        }
    }

    return (
        <div style={{
            minHeight: '100vh',
            background: '#0f172a',
            color: '#e2e8f0',
            fontFamily: 'system-ui, sans-serif',
        }}>
            {/* Header */}
            <div style={{
                borderBottom: '1px solid #1e293b',
                padding: '16px 32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
            }}>
                <div>
                    <span style={{ fontSize: 20, fontWeight: 700, color: '#f1f5f9' }}>
                        SecurePulse
                    </span>
                    <span style={{ color: '#2563eb', marginLeft: 2 }}>.</span>
                    <span style={{ fontSize: 12, color: '#64748b', marginLeft: 12 }}>
                        AI-Powered Threat Detection
                    </span>
                </div>
                <button
                    onClick={handleAnalyze}
                    disabled={analyzing}
                    style={{
                        background: analyzing ? '#334155' : '#2563eb',
                        color: '#fff',
                        border: 'none',
                        borderRadius: 8,
                        padding: '8px 20px',
                        cursor: analyzing ? 'not-allowed' : 'pointer',
                        fontWeight: 600,
                        fontSize: 14,
                    }}
                >
                    {analyzing ? 'Analyzing...' : '⚡ Run Analysis'}
                </button>
            </div>

            <div style={{ padding: '24px 32px' }}>
                <StatsBar alerts={alerts} totalLogs={totalLogs} />
                <VolumeChart logs={allLogs} />
                {/* Tabs */}
                <div style={{ display: 'flex', gap: 4, marginBottom: 20, borderBottom: '1px solid #1e293b', paddingBottom: 0 }}>
                    {['alerts', 'logs'].map(tab => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            style={{
                                background: 'none',
                                border: 'none',
                                borderBottom: activeTab === tab ? '2px solid #2563eb' : '2px solid transparent',
                                color: activeTab === tab ? '#e2e8f0' : '#64748b',
                                padding: '8px 16px',
                                cursor: 'pointer',
                                fontSize: 14,
                                fontWeight: activeTab === tab ? 600 : 400,
                                textTransform: 'capitalize',
                            }}
                        >
                            {tab}
                        </button>
                    ))}
                </div>

                {activeTab === 'alerts' && (
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
                        <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                            <div style={{ fontSize: 13, color: '#64748b', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                                Alerts Feed
                            </div>
                            <AlertsFeed
                                alerts={alerts}
                                onSelectAlert={setSelectedAlert}
                                selectedAlert={selectedAlert}
                            />
                        </div>
                        <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                            <div style={{ fontSize: 13, color: '#64748b', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                                AI Analysis
                            </div>
                            <ExplainPanel alert={selectedAlert} />
                        </div>
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                        <div style={{ fontSize: 13, color: '#64748b', marginBottom: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
                            Log Viewer
                        </div>
                        <LogViewer />
                    </div>
                )}
            </div>
        </div>
    )
}