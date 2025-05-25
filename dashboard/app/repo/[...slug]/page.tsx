'use client'
import useSWR from 'swr'
import { LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export default function RepoPage({ params }: { params: { slug: string } }) {
  const { data } = useSWR(
    `${process.env.NEXT_PUBLIC_API}/deltas/${params.slug}?days=30`,
    fetcher
  )
  if (!data) return <p className="p-4">Loading…</p>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">{params.slug}</h1>
      <LineChart width={600} height={240} data={data}>
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="kwh" strokeWidth={2} dot={false} />
      </LineChart>
    </div>
  )
}
