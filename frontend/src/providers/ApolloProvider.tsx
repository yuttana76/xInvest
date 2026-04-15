'use client';

import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';
import React from 'react';

const client = new ApolloClient({
  uri: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT || 'http://localhost:8000/graphql',
  cache: new InMemoryCache(),
});

export function AppApolloProvider({ children }: { children: React.ReactNode }) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>;
}
