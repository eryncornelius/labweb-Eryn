import React from 'react';

const StudentDashboard = () => {
  const user = JSON.parse(localStorage.getItem('user'));

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Student Dashboard</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
            <div className="text-center">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Welcome, {user?.full_name}!</h2>
              <p className="text-gray-600">This is your student dashboard. Here you can access your courses, assignments, and grades.</p>
              {/* Add more student-specific content here */}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default StudentDashboard;
