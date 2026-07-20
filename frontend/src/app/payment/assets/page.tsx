'use client';

import React, { useState } from 'react';
import { useAssets, useAssetDepreciationEntries } from '@/hooks/usePayment';
import { Boxes, ChevronDown, ChevronUp } from 'lucide-react';

export default function AssetsPage() {
  const { data: assets, isLoading, error } = useAssets();
  const [expandedId, setExpandedId] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Fixed Assets</h1>
        <p className="text-sm text-gray-500 mt-1">Assets capitalized from payment vouchers and their depreciation schedule</p>
      </div>

      {error && (
        <div className="p-8 text-center bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/20">
          <p className="text-red-600 dark:text-red-400">Error loading assets</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500 uppercase font-semibold text-xs border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4">Asset Code</th>
                <th className="px-6 py-4">Name</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Purchase Price</th>
                <th className="px-6 py-4">Purchase Date</th>
                <th className="px-6 py-4">Depreciation Rate</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  </td>
                </tr>
              ) : assets?.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-gray-500 italic">
                    <Boxes className="w-12 h-12 mx-auto mb-3 opacity-20" />
                    No fixed assets recorded yet.
                  </td>
                </tr>
              ) : (
                assets?.map((asset) => (
                  <React.Fragment key={asset.id}>
                    <tr
                      className="hover:bg-gray-50 dark:hover:bg-gray-800/30 transition-colors cursor-pointer"
                      onClick={() => setExpandedId(expandedId === asset.id ? null : asset.id)}
                    >
                      <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">{asset.asset_code}</td>
                      <td className="px-6 py-4">{asset.name}</td>
                      <td className="px-6 py-4 text-gray-600 dark:text-gray-400">{asset.category}</td>
                      <td className="px-6 py-4">{asset.purchase_price}</td>
                      <td className="px-6 py-4 text-gray-500 text-xs">{asset.purchase_date}</td>
                      <td className="px-6 py-4">{asset.depreciation_rate_percent}%</td>
                      <td className="px-6 py-4">
                        {asset.disposed_at ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                            Disposed
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                            Active
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        {expandedId === asset.id ? (
                          <ChevronUp className="w-4 h-4 text-gray-400 inline" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-gray-400 inline" />
                        )}
                      </td>
                    </tr>
                    {expandedId === asset.id && (
                      <tr>
                        <td colSpan={8} className="px-6 pb-4 bg-gray-50 dark:bg-gray-800/20">
                          <DepreciationEntries assetId={asset.id} />
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function DepreciationEntries({ assetId }: { assetId: number }) {
  const { data: entries, isLoading } = useAssetDepreciationEntries(assetId);

  if (isLoading) {
    return <div className="py-4 text-sm text-gray-400">Loading depreciation entries...</div>;
  }

  if (!entries || entries.length === 0) {
    return <div className="py-4 text-sm text-gray-400 italic">No depreciation entries recorded.</div>;
  }

  return (
    <div className="py-4 overflow-x-auto">
      <table className="w-full text-xs border border-gray-200 dark:border-gray-800 rounded-lg overflow-hidden">
        <thead className="bg-gray-100 dark:bg-gray-800 text-gray-500">
          <tr>
            <th className="px-3 py-2 text-left">Period</th>
            <th className="px-3 py-2 text-right">Amount</th>
            <th className="px-3 py-2 text-right">Accumulated</th>
            <th className="px-3 py-2 text-center">Disallowed Expense</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 dark:divide-gray-800 bg-white dark:bg-gray-900">
          {entries.map((entry) => (
            <tr key={entry.id}>
              <td className="px-3 py-2">{entry.period}</td>
              <td className="px-3 py-2 text-right">{entry.amount}</td>
              <td className="px-3 py-2 text-right">{entry.accumulated_amount}</td>
              <td className="px-3 py-2 text-center">{entry.is_disallowed_expense ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
