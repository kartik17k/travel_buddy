"""Admin routes for database management and viewing."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Form
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.models.database import User as DBUser, Itinerary as DBItinerary
from app.api.dependencies import get_current_active_user

router = APIRouter()


@router.get("/users", response_class=HTMLResponse)
async def view_users_html(db: Session = Depends(get_db)):
    """View all users in HTML format."""
    users = db.query(DBUser).all()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Buddy - Users Database</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .header { color: #333; margin-bottom: 20px; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
            .nav a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1 class="header">🗄️ Travel Buddy Database - Users</h1>
        <div class="nav">
            <a href="/admin/users">👥 Users</a>
            <a href="/admin/itineraries">🗺️ Itineraries</a>
            <a href="/admin/stats">📊 Statistics</a>
            <a href="/docs">📖 API Docs</a>
        </div>
        <h2>Users Table ({} records)</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Email</th>
                    <th>Full Name</th>
                    <th>Active</th>
                    <th>Created At</th>
                    <th>Last Login</th>
                    <th>Itineraries Count</th>
                </tr>
            </thead>
            <tbody>
    """.format(len(users))
    
    for user in users:
        itinerary_count = db.query(DBItinerary).filter(DBItinerary.user_id == user.id).count()
        html_content += f"""
                <tr>
                    <td>{user.id}</td>
                    <td>{user.email}</td>
                    <td>{user.full_name or 'N/A'}</td>
                    <td>{'✅ Yes' if user.is_active else '❌ No'}</td>
                    <td>{user.created_at.strftime('%Y-%m-%d %H:%M') if user.created_at else 'N/A'}</td>
                    <td>{user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else 'Never'}</td>
                    <td>{itinerary_count}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html_content


@router.get("/itineraries", response_class=HTMLResponse)
async def view_itineraries_html(db: Session = Depends(get_db)):
    """View all itineraries in HTML format."""
    itineraries = db.query(DBItinerary).join(DBUser).all()
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Buddy - Itineraries Database</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .header { color: #333; margin-bottom: 20px; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
            .nav a:hover { text-decoration: underline; }
            .data-cell { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        </style>
    </head>
    <body>
        <h1 class="header">🗄️ Travel Buddy Database - Itineraries</h1>
        <div class="nav">
            <a href="/admin/users">👥 Users</a>
            <a href="/admin/itineraries">🗺️ Itineraries</a>
            <a href="/admin/stats">📊 Statistics</a>
            <a href="/docs">📖 API Docs</a>
        </div>
        <h2>Itineraries Table ({} records)</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>User Email</th>
                    <th>From</th>
                    <th>To</th>
                    <th>Dates</th>
                    <th>Budget</th>
                    <th>Model</th>
                    <th>Created At</th>
                </tr>
            </thead>
            <tbody>
    """.format(len(itineraries))
    
    for itinerary in itineraries:
        html_content += f"""
                <tr>
                    <td>{itinerary.id}</td>
                    <td>{itinerary.user.email}</td>
                    <td>{itinerary.from_location}</td>
                    <td>{itinerary.to_location}</td>
                    <td class="data-cell">{itinerary.dates}</td>
                    <td>${itinerary.budget}</td>
                    <td>{itinerary.model_used}</td>
                    <td>{itinerary.created_at.strftime('%Y-%m-%d %H:%M') if itinerary.created_at else 'N/A'}</td>
                </tr>
        """
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html_content


@router.get("/stats", response_class=HTMLResponse)
async def view_stats_html(db: Session = Depends(get_db)):
    """View database statistics in HTML format."""
    
    # Get statistics
    total_users = db.query(DBUser).count()
    active_users = db.query(DBUser).filter(DBUser.is_active == True).count()
    total_itineraries = db.query(DBItinerary).count()
    
    # Get popular destinations
    popular_destinations = db.execute(text("""
        SELECT to_location, COUNT(*) as count 
        FROM itineraries 
        GROUP BY to_location 
        ORDER BY count DESC 
        LIMIT 5
    """)).fetchall()
    
    # Get model usage
    model_usage = db.execute(text("""
        SELECT model_used, COUNT(*) as count 
        FROM itineraries 
        GROUP BY model_used 
        ORDER BY count DESC
    """)).fetchall()
    
    # Calculate average budget
    avg_budget = db.execute(text("SELECT AVG(budget) as avg_budget FROM itineraries")).fetchone()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Buddy - Database Statistics</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ color: #333; margin-bottom: 20px; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
            .nav a:hover {{ text-decoration: underline; }}
            .stat-card {{ 
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 20px; 
                margin: 10px; 
                display: inline-block; 
                min-width: 200px; 
                text-align: center;
                background-color: #f9f9f9;
            }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .chart-container {{ margin: 20px 0; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1 class="header">🗄️ Travel Buddy Database - Statistics</h1>
        <div class="nav">
            <a href="/admin/users">👥 Users</a>
            <a href="/admin/itineraries">🗺️ Itineraries</a>
            <a href="/admin/stats">📊 Statistics</a>
            <a href="/docs">📖 API Docs</a>
        </div>
        
        <h2>📊 Overview</h2>
        <div class="stat-card">
            <div class="stat-number">{total_users}</div>
            <div class="stat-label">Total Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{active_users}</div>
            <div class="stat-label">Active Users</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{total_itineraries}</div>
            <div class="stat-label">Total Itineraries</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">${avg_budget[0]:.0f if avg_budget[0] else 0}</div>
            <div class="stat-label">Average Budget</div>
        </div>
        
        <h2>🌍 Popular Destinations</h2>
        <table>
            <thead>
                <tr><th>Destination</th><th>Count</th></tr>
            </thead>
            <tbody>
    """
    
    for dest in popular_destinations:
        html_content += f"<tr><td>{dest[0]}</td><td>{dest[1]}</td></tr>"
    
    html_content += """
            </tbody>
        </table>
        
        <h2>🤖 AI Model Usage</h2>
        <table>
            <thead>
                <tr><th>Model</th><th>Usage Count</th></tr>
            </thead>
            <tbody>
    """
    
    for model in model_usage:
        html_content += f"<tr><td>{model[0]}</td><td>{model[1]}</td></tr>"
    
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html_content


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(db: Session = Depends(get_db)):
    """Main admin dashboard."""
    total_users = db.query(DBUser).count()
    total_itineraries = db.query(DBItinerary).count()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Buddy - Admin Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ color: #333; margin-bottom: 30px; text-align: center; }}
            .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
            .dashboard-card {{ 
                background: white; 
                border-radius: 12px; 
                padding: 25px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                text-align: center;
                transition: transform 0.2s;
            }}
            .dashboard-card:hover {{ transform: translateY(-5px); }}
            .card-icon {{ font-size: 3em; margin-bottom: 15px; }}
            .card-title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
            .card-description {{ color: #666; margin-bottom: 20px; }}
            .card-button {{ 
                background-color: #007bff; 
                color: white; 
                padding: 10px 20px; 
                border: none; 
                border-radius: 6px; 
                text-decoration: none; 
                display: inline-block;
                transition: background-color 0.2s;
            }}
            .card-button:hover {{ background-color: #0056b3; }}
            .stats {{ margin: 20px 0; text-align: center; }}
            .stat-item {{ display: inline-block; margin: 0 20px; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; }}
        </style>
    </head>
    <body>
        <h1 class="header">🗄️ Travel Buddy Admin Dashboard</h1>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{total_users}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{total_itineraries}</div>
                <div class="stat-label">Total Itineraries</div>
            </div>
        </div>
        
        <div class="dashboard-grid">
            <div class="dashboard-card">
                <div class="card-icon">👥</div>
                <div class="card-title">Users Management</div>
                <div class="card-description">View and manage user accounts</div>
                <a href="/admin/users" class="card-button">View Users</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">🗺️</div>
                <div class="card-title">Itineraries</div>
                <div class="card-description">Browse all generated travel itineraries</div>
                <a href="/admin/itineraries" class="card-button">View Itineraries</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">📊</div>
                <div class="card-title">Statistics</div>
                <div class="card-description">View usage statistics and analytics</div>
                <a href="/admin/stats" class="card-button">View Stats</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">📖</div>
                <div class="card-title">API Documentation</div>
                <div class="card-description">Interactive API documentation</div>
                <a href="/docs" class="card-button">View Docs</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">🔧</div>
                <div class="card-title">Database Tools</div>
                <div class="card-description">Direct database access and tools</div>
                <a href="/admin/sql" class="card-button">SQL Console</a>
            </div>
            
            <div class="dashboard-card">
                <div class="card-icon">🏠</div>
                <div class="card-title">Main App</div>
                <div class="card-description">Return to the main application</div>
                <a href="/" class="card-button">Go to App</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


@router.get("/sql", response_class=HTMLResponse)
async def sql_console():
    """Simple SQL console interface."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Travel Buddy - SQL Console</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { color: #333; margin-bottom: 20px; }
            .nav { margin-bottom: 20px; }
            .nav a { margin-right: 15px; text-decoration: none; color: #007bff; }
            .nav a:hover { text-decoration: underline; }
            .sql-form { margin: 20px 0; }
            .sql-input { width: 100%; height: 200px; font-family: monospace; padding: 10px; border: 1px solid #ddd; }
            .sql-button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .sql-button:hover { background-color: #0056b3; }
            .result-area { margin-top: 20px; padding: 10px; background-color: #f8f9fa; border: 1px solid #ddd; }
            .warning { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 4px; }
        </style>
    </head>
    <body>
        <h1 class="header">🗄️ Travel Buddy Database - SQL Console</h1>
        <div class="nav">
            <a href="/admin/dashboard">🏠 Dashboard</a>
            <a href="/admin/users">👥 Users</a>
            <a href="/admin/itineraries">🗺️ Itineraries</a>
            <a href="/admin/stats">📊 Statistics</a>
        </div>
        
        <div class="warning">
            ⚠️ <strong>Warning:</strong> This is a direct SQL interface. Use with caution in production environments.
        </div>
        
        <div class="sql-form">
            <h3>Execute SQL Query</h3>
            <form method="post" action="/admin/execute-sql">
                <textarea name="sql_query" class="sql-input" placeholder="Enter your SQL query here...
Example:
SELECT * FROM users LIMIT 10;
SELECT COUNT(*) FROM itineraries;
SELECT u.email, COUNT(i.id) as itinerary_count 
FROM users u 
LEFT JOIN itineraries i ON u.id = i.user_id 
GROUP BY u.id;"></textarea>
                <br><br>
                <button type="submit" class="sql-button">Execute Query</button>
            </form>
        </div>
        
        <div class="result-area">
            <h3>Quick Queries</h3>
            <p>Try these common queries:</p>
            <ul>
                <li><code>SELECT * FROM users;</code> - View all users</li>
                <li><code>SELECT * FROM itineraries;</code> - View all itineraries</li>
                <li><code>SELECT COUNT(*) FROM users WHERE is_active = 1;</code> - Count active users</li>
                <li><code>SELECT to_location, COUNT(*) FROM itineraries GROUP BY to_location;</code> - Popular destinations</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html_content


@router.post("/execute-sql", response_class=HTMLResponse)
async def execute_sql(sql_query: str = Form(...), db: Session = Depends(get_db)):
    """Execute SQL query and return results."""
    try:
        # Execute the query
        result = db.execute(text(sql_query))
        
        # Handle different query types
        if sql_query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
            rows = result.fetchall()
            columns = result.keys() if hasattr(result, 'keys') else []
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Travel Buddy - SQL Results</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ color: #333; margin-bottom: 20px; }}
                    .nav {{ margin-bottom: 20px; }}
                    .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
                    .nav a:hover {{ text-decoration: underline; }}
                    .query-box {{ background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; margin: 10px 0; font-family: monospace; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; margin: 10px 0; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1 class="header">🗄️ Travel Buddy Database - SQL Results</h1>
                <div class="nav">
                    <a href="/admin/dashboard">🏠 Dashboard</a>
                    <a href="/admin/sql">🔧 SQL Console</a>
                    <a href="/admin/users">👥 Users</a>
                    <a href="/admin/itineraries">🗺️ Itineraries</a>
                </div>
                
                <h2>Executed Query:</h2>
                <div class="query-box">{sql_query}</div>
                
                <div class="success">✅ Query executed successfully. Found {len(rows)} rows.</div>
                
                <h2>Results:</h2>
            """
            
            if rows:
                html_content += """
                <table>
                    <thead>
                        <tr>
                """
                
                for col in columns:
                    html_content += f"<th>{col}</th>"
                
                html_content += """
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for row in rows:
                    html_content += "<tr>"
                    for cell in row:
                        html_content += f"<td>{cell}</td>"
                    html_content += "</tr>"
                
                html_content += """
                    </tbody>
                </table>
                """
            else:
                html_content += "<p>No results found.</p>"
            
            html_content += """
            </body>
            </html>
            """
            
        else:
            # For INSERT, UPDATE, DELETE queries
            db.commit()
            affected_rows = result.rowcount if hasattr(result, 'rowcount') else 0
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Travel Buddy - SQL Results</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ color: #333; margin-bottom: 20px; }}
                    .nav {{ margin-bottom: 20px; }}
                    .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
                    .nav a:hover {{ text-decoration: underline; }}
                    .query-box {{ background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; margin: 10px 0; font-family: monospace; }}
                    .success {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 10px; margin: 10px 0; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <h1 class="header">🗄️ Travel Buddy Database - SQL Results</h1>
                <div class="nav">
                    <a href="/admin/dashboard">🏠 Dashboard</a>
                    <a href="/admin/sql">🔧 SQL Console</a>
                    <a href="/admin/users">👥 Users</a>
                    <a href="/admin/itineraries">🗺️ Itineraries</a>
                </div>
                
                <h2>Executed Query:</h2>
                <div class="query-box">{sql_query}</div>
                
                <div class="success">✅ Query executed successfully. {affected_rows} rows affected.</div>
            </body>
            </html>
            """
        
        return html_content
        
    except Exception as e:
        # Error handling
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Travel Buddy - SQL Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ color: #333; margin-bottom: 20px; }}
                .nav {{ margin-bottom: 20px; }}
                .nav a {{ margin-right: 15px; text-decoration: none; color: #007bff; }}
                .nav a:hover {{ text-decoration: underline; }}
                .query-box {{ background-color: #f8f9fa; padding: 10px; border: 1px solid #ddd; margin: 10px 0; font-family: monospace; }}
                .error {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 10px; margin: 10px 0; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1 class="header">🗄️ Travel Buddy Database - SQL Error</h1>
            <div class="nav">
                <a href="/admin/dashboard">🏠 Dashboard</a>
                <a href="/admin/sql">🔧 SQL Console</a>
                <a href="/admin/users">👥 Users</a>
                <a href="/admin/itineraries">🗺️ Itineraries</a>
            </div>
            
            <h2>Executed Query:</h2>
            <div class="query-box">{sql_query}</div>
            
            <div class="error">❌ Error executing query: {str(e)}</div>
            
            <p><a href="/admin/sql">← Back to SQL Console</a></p>
        </body>
        </html>
        """
        
        return html_content
