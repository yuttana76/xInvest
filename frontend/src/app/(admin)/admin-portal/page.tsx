import React from 'react';
import { Search, Filter, MoreHorizontal, UserCheck, UserX, AlertCircle } from 'lucide-react';
import { Button } from '@/components/Button';

const customers = [
  { id: '1', name: 'John Doe', email: 'john@example.com', status: 'Healthy', risk: 'Low', value: '$124,592' },
  { id: '2', name: 'Sarah Smith', email: 'sarah@example.com', status: 'Rebalance', risk: 'Medium', value: '$85,200' },
  { id: '3', name: 'Michael Brown', email: 'm.brown@example.com', status: 'Critical', risk: 'High', value: '$240,150' },
  { id: '4', name: 'Emma Wilson', email: 'emma.w@example.com', status: 'Healthy', risk: 'Low', value: '$42,300' },
  { id: '5', name: 'James Davis', email: 'james@example.com', status: 'Rebalance', risk: 'Medium', value: '$110,000' },
];

const StatusBadge = ({ status }: { status: string }) => {
  const styles: Record<string, string> = {
    'Healthy': 'bg-primary/10 text-primary',
    'Rebalance': 'bg-secondary/10 text-secondary',
    'Critical': 'bg-rose-500/10 text-rose-500',
  };
  
  const icons: Record<string, React.ReactNode> = {
    'Healthy': <UserCheck size={14} />,
    'Rebalance': <AlertCircle size={14} />,
    'Critical': <UserX size={14} />,
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[status]}`}>
      {icons[status]}
      {status}
    </span>
  );
};

export default function AdminPortal() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Customer Management</h1>
        <p className="text-slate-400 mt-1">Monitor and manage all investor portfolios and risk models.</p>
      </div>

      {/* Admin Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { label: "Total Assets Under Mgmt", value: "$4.2M", change: "+$240k this month" },
          { label: "Active Investors", value: "1,248", change: "+12 today" },
          { label: "Avg Portfolio Growth", value: "12.4%", change: "+2.1% YoY" }
        ].map((stat, i) => (
          <div key={i} className="glass p-6 rounded-2xl border border-white/5">
            <p className="text-sm text-slate-400">{stat.label}</p>
            <h3 className="text-2xl font-bold mt-1">{stat.value}</h3>
            <p className="text-xs text-primary mt-2">{stat.change}</p>
          </div>
        ))}
      </div>

      {/* Table Section */}
      <div className="glass rounded-2xl border border-white/5 overflow-hidden">
        <div className="p-6 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
            <input 
              type="text" 
              placeholder="Search customers by name or email..." 
              className="w-full bg-white/5 border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm outline-none focus:border-primary/50 transition-colors"
            />
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" className="gap-2">
              <Filter size={16} />
              Filters
            </Button>
            <Button size="sm">Export Data</Button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5">
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk Profile</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Portfolio Value</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {customers.map((c) => (
                <tr key={c.id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="font-medium">{c.name}</div>
                    <div className="text-xs text-slate-500">{c.email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm">{c.risk}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm font-medium">{c.value}</span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button className="p-2 text-slate-500 hover:text-white transition-colors">
                      <MoreHorizontal size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
