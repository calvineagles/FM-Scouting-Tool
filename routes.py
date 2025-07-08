import os
from flask import render_template, request, jsonify
from data import load_player_data, list_html_files
from werkzeug.utils import secure_filename

def init_routes(app):
    """Initialize all routes for the Flask app"""
    UPLOAD_FOLDER = 'uploaded_htmls'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    @app.route('/')
    def index():
        """Main page route"""
        return render_template('index.html')

    @app.route('/api/upload_html', methods=['POST'])
    def upload_html():
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'})
        if not file.filename.lower().endswith('.html'):
            return jsonify({'success': False, 'error': 'Only .html files allowed'})
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        return jsonify({'success': True, 'filename': save_path})

    @app.route('/api/html_files')
    def get_html_files():
        """API endpoint to get available HTML files"""
        files = list_html_files()
        return jsonify(files)

    @app.route('/api/positions')
    def get_positions():
        filename = request.args.get('filename', 'All_Players.html')
        df = load_player_data(filename)
        if df.empty:
            return jsonify([])
        positions = df['Best Pos'].dropna().unique().tolist()
        return jsonify(positions)

    @app.route('/api/teams')
    def get_teams():
        filename = request.args.get('filename', 'All_Players.html')
        df = load_player_data(filename)
        if df.empty:
            return jsonify([])
        teams = sorted(df['Club'].dropna().unique().tolist())
        return jsonify(teams)

    @app.route('/api/stats')
    def get_stats():
        filename = request.args.get('filename', 'All_Players.html')
        df = load_player_data(filename)
        if df.empty:
            return jsonify([])
        # Get columns from 'Aer A/90' to 'xG'
        start_col = 'Aer A/90'
        end_col = 'xG'
        all_columns = df.columns.tolist()
        start_idx = all_columns.index(start_col) if start_col in all_columns else 0
        end_idx = all_columns.index(end_col) + 1 if end_col in all_columns else len(all_columns)
        stats_columns = all_columns[start_idx:end_idx]
        return jsonify(stats_columns)

    @app.route('/api/compare', methods=['POST'])
    def compare_players():
        try:
            data = request.get_json()
            filename = data.get('filename', 'All_Players.html')
            position = data.get('position')
            stat1 = data.get('stat1')
            stat2 = data.get('stat2')
            df = load_player_data(filename)
            if df.empty:
                return jsonify({'error': 'No data available'})
            # Filter by position
            if position and position != 'All':
                filtered_df = df[df['Best Pos'] == position].copy()
            else:
                filtered_df = df.copy()
            # Remove rows with missing data for selected stats
            filtered_df = filtered_df.dropna(subset=[stat1, stat2])
            if filtered_df.empty:
                return jsonify({'error': 'No data available for selected criteria'})
            # Calculate averages for axis lines
            avg_stat1 = filtered_df[stat1].mean()
            avg_stat2 = filtered_df[stat2].mean()
            # Calculate medians for trend lines
            median_stat1 = filtered_df[stat1].median()
            median_stat2 = filtered_df[stat2].median()
            # Prepare data for plotting
            fm_attributes = [
                # Technical
                'Cor', 'Cro', 'Dri', 'Fin', 'Fir', 'Fre', 'Hea', 'Lon', 'L Th', 'Mar', 'Pas', 'Pen', 'Tck', 'Tec',
                # Mental
                'Agg', 'Ant', 'Bra', 'Cmp', 'Cnt', 'Dec', 'Det', 'Fla', 'Ldr', 'OtB', 'Pos', 'Tea', 'Vis', 'Wor',
                # Physical
                'Acc', 'Agi', 'Bal', 'Jum', 'Nat', 'Pac', 'Sta', 'Str'
            ]
            plot_data = []
            for _, row in filtered_df.iterrows():
                # Ensure x and y are always float and not Series
                x_val = row[stat1]
                y_val = row[stat2]
                if hasattr(x_val, 'iloc'):
                    x_val = x_val.iloc[0]
                if hasattr(y_val, 'iloc'):
                    y_val = y_val.iloc[0]
                player_data = {
                    'name': str(row.get('Name', '')),
                    'club': str(row.get('Club', '')),
                    'position': str(row.get('Best Pos', '')),
                    'age': str(row.get('Age', '')),
                    'transfer_value': str(row.get('Transfer Value', '')),
                    'wage': str(row.get('Wage', '')),
                    'x': float(x_val) if x_val not in [None, ''] else 0,
                    'y': float(y_val) if y_val not in [None, ''] else 0,
                    'attributes': {}
                }
                for attr in fm_attributes:
                    value = row.get(attr, '')
                    if hasattr(value, 'iloc'):
                        value = value.iloc[0]
                    player_data['attributes'][attr] = str(value) if value is not None else ''
                plot_data.append(player_data)
            return jsonify({
                'data': plot_data,
                'avg_x': avg_stat1,
                'avg_y': avg_stat2,
                'median_x': median_stat1,
                'median_y': median_stat2,
                'stat1': stat1,
                'stat2': stat2
            })
        except Exception as e:
            print(f"Error in /api/compare: {e}")
            return jsonify({'error': str(e)}), 500 