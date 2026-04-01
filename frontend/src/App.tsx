import { useChatStore } from "./stores/chatStore";
import AppLayout from "./components/layout/AppLayout";
import DashboardPage from "./components/dashboard/DashboardPage";
import LibraryPage from "./components/library/LibraryPage";
import IntegrationsPage from "./components/integrations/IntegrationsPage";
import ProfilePage from "./components/profile/ProfilePage";
import SupportPage from "./components/support/SupportPage";
import ErrorBoundary from "./components/common/ErrorBoundary";
import ToastProvider from "./components/common/Toast";

function PageRouter() {
  const currentPage = useChatStore((s) => s.currentPage);

  switch (currentPage) {
    case "library":
      return <LibraryPage />;
    case "integrations":
      return <IntegrationsPage />;
    case "profile":
      return <ProfilePage />;
    case "support":
      return <SupportPage />;
    case "dashboard":
    default:
      return <DashboardPage />;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <AppLayout>
        <PageRouter />
      </AppLayout>
      <ToastProvider />
    </ErrorBoundary>
  );
}

export default App;
