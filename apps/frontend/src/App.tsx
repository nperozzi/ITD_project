import { useMemo, useState } from 'react';
import { AppLayout } from './components/layout';
import {
  DashboardPage,
  StoresPage,
  GatewaysPage,
  ShelfLocationsPage,
  ProductsPage,
  TagsPage,
  PromotionsPage,
} from './components/pages';
import {
  useGateways,
  useProducts,
  usePromotions,
  useShelfLocations,
  useStores,
  useTags,
} from './hooks/useBackendData';
import type { NavigationKey } from './types';

function LoadingState(): JSX.Element {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">Loading workspace data...</p>
      <p className="mt-1 text-base font-medium">Preparing your ESL operations dashboard</p>
    </div>
  );
}

function ErrorState({ message }: { message: string }): JSX.Element {
  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">Unable to load workspace data</p>
      <p className="mt-1 text-base font-medium">{message}</p>
    </div>
  );
}

export default function App(): JSX.Element {
  const [activePage, setActivePage] = useState<NavigationKey>('dashboard');

  // Load each dashboard collection independently from backend.
  const { data: stores, error: storesError } = useStores();
  const { data: gateways, error: gatewaysError } = useGateways();
  const { data: shelfLocations, error: shelfLocationsError } = useShelfLocations();
  const { data: products, error: productsError } = useProducts();
  const { data: tags, error: tagsError } = useTags();
  const { data: promotions, error: promotionsError } = usePromotions();

  const content = useMemo(() => {
    // Show the first request error so the user has a clear actionable message.
    const firstError =
      storesError ??
      gatewaysError ??
      shelfLocationsError ??
      productsError ??
      tagsError ??
      promotionsError;

    if (firstError) {
      return <ErrorState message={firstError.message} />;
    }

    // Keep a single loading state until all required datasets are available.
    if (!stores || !gateways || !shelfLocations || !products || !tags || !promotions) {
      return <LoadingState />;
    }

    switch (activePage) {
      case 'dashboard':
        return (
          <DashboardPage
            stores={stores}
            gateways={gateways}
            shelfLocations={shelfLocations}
            products={products}
            tags={tags}
            promotions={promotions}
          />
        );
      case 'stores':
        return <StoresPage stores={stores} />;
      case 'gateways':
        return <GatewaysPage gateways={gateways} />;
      case 'shelf-locations':
        return <ShelfLocationsPage shelfLocations={shelfLocations} />;
      case 'products':
        return <ProductsPage products={products} />;
      case 'tags':
        return <TagsPage tags={tags} />;
      case 'promotions':
        return <PromotionsPage promotions={promotions} />;
      default:
        return <LoadingState />;
    }
  }, [
    activePage,
    stores,
    gateways,
    shelfLocations,
    products,
    tags,
    promotions,
    storesError,
    gatewaysError,
    shelfLocationsError,
    productsError,
    tagsError,
    promotionsError,
  ]);

  return (
    <AppLayout active={activePage} onChange={setActivePage}>
      {content}
    </AppLayout>
  );
}
