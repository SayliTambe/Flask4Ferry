document.addEventListener('DOMContentLoaded', () => {
  // Initialize event listeners
  document.getElementById('addPromotionBtn').addEventListener('click', showAddPromotion);
  document.getElementById('modifyPromotionBtn').addEventListener('click', showModifyPromotionOptions);
  document.getElementById('deletePromotionBtn').addEventListener('click', showDeletePromotionOptions);
  document.getElementById('viewPromotionsBtn').addEventListener('click', showPromotions);

  document.getElementById('promotionForm').addEventListener('submit', (e) => {
    e.preventDefault();
    addNewPromotion();
  });

  document.getElementById('modifyForm').addEventListener('submit', (e) => {
    e.preventDefault();
    saveModifiedPromotion();
  });
});

function toggleSubMenu() {
  const submenu = document.getElementById('submenu');
  submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
}

function showAddPromotion() {
  hideAllSections();
  document.getElementById('promotionForm').style.display = 'flex';
}

function showModifyPromotionOptions() {
  hideAllSections();
  document.getElementById('codeList').style.display = 'flex';

  fetch('/promotions')
    .then(response => response.json())
    .then(data => {
      const codeList = document.getElementById('codeList');
      codeList.innerHTML = '<h2>Select a Promotion to Modify</h2>';

      data.promotions.forEach(promotion => {
        const button = document.createElement('button');
        button.textContent = promotion.code;
        button.addEventListener('click', () => showModifyPromotion(promotion.code));
        codeList.appendChild(button);
      });
    })
    .catch(error => console.error('Error:', error));
}

function showModifyPromotion(code) {
  hideAllSections();
  document.getElementById('modifyForm').style.display = 'flex';

  fetch(`/promotions`)
    .then(response => response.json())
    .then(data => {
      const promotion = data.promotions.find(p => p.code === code);
      if (promotion) {
        document.getElementById('modifyTitle').value = promotion.title;
        document.getElementById('modifyCode').value = promotion.code;
        document.getElementById('modifyFromDate').value = promotion.from_date;
        document.getElementById('modifyToDate').value = promotion.to_date;
        document.getElementById('modifyPercentage').value = promotion.percentage;
      }
    })
    .catch(error => console.error('Error:', error));
}

function showDeletePromotionOptions() {
  hideAllSections();
  document.getElementById('codeList').style.display = 'flex';

  fetch('/promotions')
    .then(response => response.json())
    .then(data => {
      const codeList = document.getElementById('codeList');
      codeList.innerHTML = '<h2>Select a Promotion to Delete</h2>';

      data.promotions.forEach(promotion => {
        const button = document.createElement('button');
        button.textContent = promotion.code;
        button.addEventListener('click', () => removePromoCode(promotion.code));
        codeList.appendChild(button);
      });
    })
    .catch(error => console.error('Error:', error));
}

function addNewPromotion() {
  const title = document.getElementById('promotionTitle').value;
  const code = document.getElementById('promotionCode').value;
  const fromDate = document.getElementById('fromDate').value;
  const toDate = document.getElementById('toDate').value;
  const percentage = document.getElementById('percentage').value;

  if (title && code && fromDate && toDate && percentage) {
    const newPromotion = {
      title: title,
      code: code,
      from_date: fromDate,
      to_date: toDate,
      percentage: percentage
    };

    fetch('/add_promotion', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newPromotion)
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
      document.getElementById('promotionForm').reset();
      showPromotions();
    })
    .catch(error => console.error('Error:', error));
  } else {
    alert("All fields are required.");
  }
}

function saveModifiedPromotion() {
  const title = document.getElementById('modifyTitle').value;
  const code = document.getElementById('modifyCode').value;
  const fromDate = document.getElementById('modifyFromDate').value;
  const toDate = document.getElementById('modifyToDate').value;
  const percentage = document.getElementById('modifyPercentage').value;

  if (title && fromDate && toDate && percentage) {
    const updatedPromotion = {
      title: title,
      from_date: fromDate,
      to_date: toDate,
      percentage: percentage
    };

    fetch(`/modify_promotion/${code}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(updatedPromotion)
    })
    .then(response => response.json())
    .then(data => {
      alert(data.message);
      showPromotions();
    })
    .catch(error => console.error('Error:', error));
  } else {
    alert("All fields are required.");
  }
}

function removePromoCode(code) {
  fetch(`/delete_promotion/${code}`, {
    method: 'DELETE'
  })
  .then(response => response.json())
  .then(data => {
    alert(data.message);
    showPromotions();
  })
  .catch(error => console.error('Error:', error));
}

function showPromotions() {
  hideAllSections();
  document.getElementById('promotions').style.display = 'block';

  fetch('/promotions')
    .then(response => response.json())
    .then(data => {
      const promotionTableBody = document.getElementById('promotionTableBody');
      promotionTableBody.innerHTML = '';

      if (data.promotions.length === 0) {
        promotionTableBody.innerHTML = '<tr><td colspan="6">No promotions available.</td></tr>';
      } else {
        data.promotions.forEach(promotion => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${promotion.title}</td>
            <td>${promotion.code}</td>
            <td>${promotion.from_date}</td>
            <td>${promotion.to_date}</td>
            <td>${promotion.percentage}%</td>
            <td>
              <button onclick="removePromoCode('${promotion.code}')">Delete</button>
            </td>
          `;
          promotionTableBody.appendChild(row);
        });
      }
    })
    .catch(error => console.error('Error:', error));
}

function hideAllSections() {
  document.getElementById('promotionForm').style.display = 'none';
  document.getElementById('modifyForm').style.display = 'none';
  document.getElementById('promotions').style.display = 'none';
  document.getElementById('codeList').style.display = 'none';
}
