import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from './components/Layout'
import { Dashboard } from './components/Dashboard'
import { SubnetDetail } from './components/SubnetDetail'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/subnet/:netuid" element={<SubnetDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
