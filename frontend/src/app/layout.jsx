import './globals.css';
import Navbar from '../components/layout/Navbar';
import Sidebar from '../components/layout/Sidebar';
import ToastProvider from '../components/providers/ToastProvider';

export const metadata = {
  title: 'Uplift - AI Government Scheme Recommender',
  description: 'Agentic AI-powered discovery and eligibility evaluator for central and state government schemes across India.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        <div className="min-h-screen flex flex-col bg-gray-50 text-gray-900">
          <Navbar />
          <div className="flex-1 flex overflow-hidden">
            <Sidebar />
            <main className="flex-1 overflow-y-auto bg-gray-50/50">
              {children}
            </main>
          </div>
        </div>
        <ToastProvider />
      </body>
    </html>
  );
}
