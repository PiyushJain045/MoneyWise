// learn.js

const contentData = {
    investing: [
      { type: 'Course', title: 'Stock Market Basics', duration: '4 weeks', level: 'Beginner' },
      { type: 'Course', title: 'ETF Investing Mastery', duration: '6 weeks', level: 'Intermediate' },
      { type: 'Book', title: 'The Intelligent Investor' },
      { type: 'Book', title: 'A Random Walk Down Wall Street' }
    ],
    budgeting: [
      { type: 'Course', title: 'Smart Budgeting 101', duration: '3 weeks', level: 'Beginner' },
      { type: 'Course', title: 'Advanced Household Budgeting', duration: '5 weeks', level: 'Advanced' },
      { type: 'Book', title: 'Your Money or Your Life' },
      { type: 'Book', title: 'The Total Money Makeover' }
    ],
    trading: [
      { type: 'Course', title: 'Intraday Trading Basics', duration: '2 weeks', level: 'Beginner' },
      { type: 'Course', title: 'Options Trading Advanced', duration: '4 weeks', level: 'Advanced' },
      { type: 'Book', title: 'Technical Analysis of the Financial Markets' },
      { type: 'Book', title: 'Trading in the Zone' }
    ],
    taxes: [
      { type: 'Course', title: 'Understanding Tax Returns', duration: '3 weeks', level: 'Beginner' },
      { type: 'Course', title: 'Small Business Tax Strategies', duration: '4 weeks', level: 'Intermediate' },
      { type: 'Book', title: 'J.K. Lasser’s Your Income Tax' },
      { type: 'Book', title: 'Small Business Taxes For Dummies' }
    ],
    'real-estate': [
      { type: 'Course', title: 'Real Estate Investment Basics', duration: '4 weeks', level: 'Beginner' },
      { type: 'Course', title: 'Managing Rental Properties', duration: '6 weeks', level: 'Intermediate' },
      { type: 'Book', title: 'Rich Dad Poor Dad' },
      { type: 'Book', title: 'The Millionaire Real Estate Investor' }
    ]
  };
  
  document.addEventListener("DOMContentLoaded", () => {
    const topics = document.querySelectorAll(".topic:not(.coming-soon)");
    const contentArea = document.getElementById("content-area");
  
    topics.forEach(topic => {
      topic.addEventListener("click", () => {
        const selected = topic.dataset.topic;
        const data = contentData[selected];
  
        if (!data) return;
  
        contentArea.innerHTML = ""; // Clear previous content
  
        data.forEach(item => {
          const card = document.createElement("div");
          card.classList.add("card");
  
          if (item.type === "Course") {
            card.innerHTML = `
              <h4>${item.title}</h4>
              <p><strong>Duration:</strong> ${item.duration}</p>
              <p><strong>Level:</strong> ${item.level}</p>
            `;
          } else if (item.type === "Book") {
            card.innerHTML = `
              <h4>${item.title}</h4>
              <p><strong>Type:</strong> Book</p>
            `;
          }
  
          contentArea.appendChild(card);
        });
      });
    });
  });
  