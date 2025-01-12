// Utility functions
function safeValue(value) {
    return value === null || value === undefined ? "N/A" : value;
}

function displayError(message) {
    const errorDiv = document.getElementById("error");
    errorDiv.innerHTML = `<p style="color: red;">${message}</p>`;
}

// Display functions
function displayLatestStock(stock) {
    const latestStockDiv = document.getElementById("latest-stock-data");
    if (stock) {
        latestStockDiv.innerHTML = `
            <h3>Latest Stock Data</h3>
            <p>Date: ${safeValue(stock.date)}</p>
            <p>Price: ${safeValue(stock.price)}</p>
            <p>EPS: ${safeValue(stock.EPS)}</p>
            <p>PER: ${safeValue(stock.PER)}</p>
        `;
    } else {
        latestStockDiv.innerHTML = `<p>No stock data found.</p>`;
    }
}

function displayAllStocks(stocks) {
    const allStocksTable = document.getElementById("all-stocks-data");
    if (stocks.length > 0) {
        allStocksTable.innerHTML = `
            <h3>All Stock Data</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Price</th>
                        <th>EPS</th>
                        <th>PER</th>
                    </tr>
                </thead>
                <tbody>
                    ${stocks
                        .map(
                            (stock) => `
                                <tr>
                                    <td>${safeValue(stock.date)}</td>
                                    <td>${safeValue(stock.price)}</td>
                                    <td>${safeValue(stock.EPS)}</td>
                                    <td>${safeValue(stock.PER)}</td>
                                </tr>
                            `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    } else {
        allStocksTable.innerHTML = `<p>No stock data found.</p>`;
    }
}

function displayBacktestResults(results) {
    const backtestDiv = document.getElementById("backtest-results");
    if (results.length > 0) {
        backtestDiv.innerHTML = `
            <h3>Backtest Results</h3>
            <table border="1">
                <thead>
                    <tr>
                        <th>Stock ID</th>
                        <th>Current Price</th>
                        <th>Median Price</th>
                        <th>T$</th>
                        <th>MP UpDown</th>
                        <th>1M MR</th>
                        <th>2M MR</th>
                        <th>3M MR</th>
                        <th>Avg.</th>
                        <th>Kelly</th>
                        <th>Verdict</th>
                        <th>1M Incident</th>
                        <th>2M Incident</th>
                        <th>3M Incident</th>
                    </tr>
                </thead>
                <tbody>
                    ${results
                        .map(
                            (result) => `
                                <tr>
                                    <td>${safeValue(result["Stock ID"])}</td>
                                    <td>${safeValue(result["C$"])}</td>
                                    <td>${safeValue(result["M$"])}</td>
                                    <td>${safeValue(result["T$"])}</td>
                                    <td>${safeValue(result["MP UpDown"])}</td>
                                    <td>${safeValue(result["1M MR"])}</td>
                                    <td>${safeValue(result["2M MR"])}</td>
                                    <td>${safeValue(result["3M MR"])}</td>
                                    <td>${safeValue(result["Avg."])}</td>
                                    <td>${safeValue(result["Kelly"])}</td>
                                    <td>${result["Verdict"] ? "Yes" : "No"}</td>
                                    <td>${safeValue(result["1M Incident"])}</td>
                                    <td>${safeValue(result["2M Incident"])}</td>
                                    <td>${safeValue(result["3M Incident"])}</td>
                                </tr>
                            `
                        )
                        .join("")}
                </tbody>
            </table>
        `;
    } else {
        backtestDiv.innerHTML = `<p>No backtest results found.</p>`;
    }
}

// Fetch the latest stock data
async function fetchLatestStock(event) {
    event.preventDefault();
    const stockId = document.getElementById("latest_stock_id").value.trim();
    if (!stockId) {
        displayError("Please enter a valid Stock ID.");
        return;
    }

    try {
        const response = await fetch(`/api/stock?stock_id=${stockId}&limit=1`);
        if (response.ok) {
            const data = await response.json();
            displayLatestStock(data[0] || null);
        } else {
            displayError("Failed to fetch the latest stock data.");
        }
    } catch (error) {
        displayError(`Error fetching latest stock data: ${error.message}`);
    }
}

// Fetch all stock data
async function fetchAllStocks(event) {
    event.preventDefault();
    const stockId = document.getElementById("fetch_stock_id").value.trim();
    const limit = parseInt(document.getElementById("limit").value, 10);
    const offset = parseInt(document.getElementById("offset").value, 10);

    if (!stockId || limit <= 0 || offset < 0) {
        displayError("Invalid input. Please ensure all fields are correctly filled.");
        return;
    }

    try {
        const response = await fetch(
            `/api/stock?stock_id=${stockId}&limit=${limit}&offset=${offset}`
        );
        if (response.ok) {
            const data = await response.json();
            displayAllStocks(data);
        } else {
            displayError("Failed to fetch all stock data.");
        }
    } catch (error) {
        displayError(`Error fetching all stock data: ${error.message}`);
    }
}

// Perform backtest
async function performBacktest(event) {
    event.preventDefault();
    const stockIds = document.getElementById("backtest_stock_ids").value
        .split(",")
        .map((id) => id.trim())
        .filter(Boolean);

    if (stockIds.length === 0) {
        displayError("Please enter at least one Stock ID.");
        return;
    }

    try {
        const response = await fetch("/api/stock/backtest", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stock_numbers: stockIds }),
        });
        if (response.ok) {
            const data = await response.json();
            displayBacktestResults(data);
        } else {
            displayError("Failed to perform backtest.");
        }
    } catch (error) {
        displayError(`Error performing backtest: ${error.message}`);
    }
}

// Process uploaded Excel file
async function processExcelFile(event) {
    event.preventDefault();
    const fileInput = document.getElementById("excelFile");
    const loadingIndicator = document.getElementById("loading-indicator");
    const file = fileInput.files[0];

    if (!file) {
        displayError("Please select an Excel file first.");
        return;
    }

    const reader = new FileReader();
    loadingIndicator.style.display = "block";

    reader.onload = function (e) {
        const data = new Uint8Array(e.target.result);
        const workbook = XLSX.read(data, { type: "array" });
        const sheetName = workbook.SheetNames[0];
        const sheetData = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName]);

        sendDataToBackend(sheetData).finally(() => {
            loadingIndicator.style.display = "none";
        });
    };

    reader.readAsArrayBuffer(file);
}

async function sendDataToBackend(data) {
    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            const data = await response.json();
            displayBacktestResults(data);
        } else {
            displayError("Failed to upload Excel data.");
        }
    } catch (error) {
        displayError(`Error uploading Excel data: ${error.message}`);
    }
}

// Event Listeners
document.getElementById("latest-stock-form").addEventListener("submit", fetchLatestStock);
document.getElementById("excel-upload-form").addEventListener("submit", processExcelFile);
document.getElementById("all-stocks-form").addEventListener("submit", fetchAllStocks);
document.getElementById("backtest-form").addEventListener("submit", performBacktest);
