from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator
from django.conf import settings
import os
import io
import base64

# Data science imports
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# HELPER UTILITIES
# ============================================================

def fig_to_base64(fig):
    """Convert a matplotlib figure to a base64-encoded PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor(), edgecolor='none')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str


def get_data_path():
    return os.path.join(settings.MEDIA_ROOT, 'rural_digital_transformation_clean.csv')


def get_model_path():
    return os.path.join(settings.MEDIA_ROOT, 'trained_model.joblib')


FEATURE_COLUMNS = [
    'broadband_penetration_pct', 'five_g_base_stations_per_100sqkm',
    'cell_phone_penetration_pct', 'road_length_km', 'mail_delivery_miles_km',
    'number_of_schools', 'ecommerce_turnover_per_capita',
    'agritech_venture_capital_million', 'ant_financial_index',
    'digital_economy_index', 'disposable_income_per_capita',
    'rural_ict_certified_labor_pct', 'returnee_entrepreneurs_per_1000',
    'education_years', 'hightech_workers_pct', 'e_participation_index',
    'blockchain_land_certificate_ratio', 'environmental_monitoring_stations',
    'terrain_ruggedness_index', 'distance_to_nearest_city_km'
]

FEATURE_LABELS = {
    'broadband_penetration_pct': 'Broadband Penetration (%)',
    'five_g_base_stations_per_100sqkm': '5G Base Stations (per 100 sq km)',
    'cell_phone_penetration_pct': 'Cell Phone Penetration (%)',
    'road_length_km': 'Road Length (km)',
    'mail_delivery_miles_km': 'Mail Delivery Miles (km)',
    'number_of_schools': 'Number of Schools',
    'ecommerce_turnover_per_capita': 'E-Commerce Turnover Per Capita',
    'agritech_venture_capital_million': 'Agritech Venture Capital (M)',
    'ant_financial_index': 'Ant Financial Index',
    'digital_economy_index': 'Digital Economy Index',
    'disposable_income_per_capita': 'Disposable Income Per Capita',
    'rural_ict_certified_labor_pct': 'Rural ICT Certified Labor (%)',
    'returnee_entrepreneurs_per_1000': 'Returnee Entrepreneurs (per 1000)',
    'education_years': 'Education Years',
    'hightech_workers_pct': 'High-Tech Workers (%)',
    'e_participation_index': 'E-Participation Index',
    'blockchain_land_certificate_ratio': 'Blockchain Land Certificate Ratio',
    'environmental_monitoring_stations': 'Env. Monitoring Stations',
    'terrain_ruggedness_index': 'Terrain Ruggedness Index',
    'distance_to_nearest_city_km': 'Distance to Nearest City (km)'
}


# ============================================================
# AUTH VIEWS  (Registration, Login, Logout)
# ============================================================

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.status = 'waiting'
            user.save()
            messages.success(request, "Account created successfully! Please wait for Admin activation before logging in.")
            return redirect('UserLogin')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'email':
                        messages.error(request, f'Email Error: {error}')
                    elif field == 'mobile':
                        messages.error(request, f'Mobile Error: {error}')
                    elif field == 'loginid':
                        messages.error(request, f'Login ID Error: {error}')
                    else:
                        messages.error(request, f'{field.title()}: {error}')
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegisterations.html', {'form': form})


def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print(f'Login attempt - LoginID: {loginid}')
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid)
            print(f'User found - Status: {check.status}')
            if check_password(pswd, check.password):
                status = check.status
                print(f'Password verified - Status: {status}')
                if status == "activated":
                    request.session['id'] = check.id
                    request.session['loggeduser'] = check.Username
                    request.session['loginid'] = loginid
                    request.session['email'] = check.email
                    print(f"Login successful - User ID: {check.id}")
                    # FIX: Use redirect instead of render to avoid
                    # NoReverseMatch crash inside UserHome template
                    return redirect('UserHome')
                else:
                    print(f'Account not activated - Status: {status}')
                    messages.warning(request, 'Your Account Not yet activated')
                    return render(request, 'UserLogin.html')
            else:
                print('Password verification failed')
                messages.warning(request, 'Invalid Login ID Or Password')
                return render(request, 'UserLogin.html')
        # FIX: Catch only DoesNotExist, not all exceptions
        except UserRegistrationModel.DoesNotExist:
            print('User not found in database')
            messages.warning(request, 'Invalid Login ID Or Password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    if 'id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard')
        return redirect('UserLogin')
    return render(request, 'users/UserHome.html', {})


def UserLogout(request):
    request.session.flush()
    messages.success(request, 'You have been successfully logged out')
    return redirect('UserLogin')


# ============================================================
# DATASET VIEW
# ============================================================

def UserDataset(request):
    if 'id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard')
        return redirect('UserLogin')

    try:
        df = pd.read_csv(get_data_path())

        search = request.GET.get('search', '')
        if search:
            mask = df.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(),
                axis=1,
            )
            df = df[mask]

        total_records = len(df)
        columns = df.columns.tolist()

        page_number = request.GET.get('page', 1)
        paginator = Paginator(df.values.tolist(), 25)
        page_obj = paginator.get_page(page_number)

        context = {
            'columns': columns,
            'page_obj': page_obj,
            'total_records': total_records,
            'total_columns': len(columns),
            'search': search,
        }
    except Exception as e:
        messages.error(request, f'Error loading dataset: {str(e)}')
        context = {}

    return render(request, 'users/UserDataset.html', context)


# ============================================================
# TRAINING VIEW
# ============================================================

def UserTraining(request):
    if 'id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard')
        return redirect('UserLogin')

    if request.method == 'POST':
        try:
            from sklearn.model_selection import train_test_split
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.tree import DecisionTreeClassifier
            from sklearn.svm import SVC
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import LabelEncoder, StandardScaler
            from sklearn.metrics import (accuracy_score, precision_score,
                                         recall_score, f1_score,
                                         confusion_matrix)
            import joblib

            # ---- Load & prepare data ----
            df = pd.read_csv(get_data_path())
            X = df[FEATURE_COLUMNS]
            y = df['rdt_level']

            le = LabelEncoder()
            y_encoded = le.fit_transform(y)

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded,
                test_size=0.2, random_state=42, stratify=y_encoded,
            )

            # ---- Train models ----
            models = {
                'Random Forest': RandomForestClassifier(
                    n_estimators=100, random_state=42),
                'Decision Tree': DecisionTreeClassifier(random_state=42),
                'SVM (RBF Kernel)': SVC(
                    kernel='rbf', random_state=42, probability=True),
                'Logistic Regression': LogisticRegression(
                    max_iter=1000, random_state=42),
            }

            results = []
            best_acc = 0
            best_model_name = ''

            for name, model in models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred,
                                       average='macro', zero_division=0)
                rec = recall_score(y_test, y_pred,
                                    average='macro', zero_division=0)
                f1 = f1_score(y_test, y_pred,
                              average='macro', zero_division=0)

                if acc > best_acc:
                    best_acc = acc
                    best_model_name = name

                results.append({
                    'name': name,
                    'accuracy': round(acc * 100, 2),
                    'precision': round(prec * 100, 2),
                    'recall': round(rec * 100, 2),
                    'f1': round(f1 * 100, 2),
                })

            # ---- Save the Random Forest model ----
            rf_model = models['Random Forest']
            joblib.dump({
                'model': rf_model,
                'scaler': scaler,
                'label_encoder': le,
                'feature_columns': FEATURE_COLUMNS,
            }, get_model_path())

            # ---- Chart 1: Performance comparison bar chart ----
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.patch.set_facecolor('#0a1628')
            ax.set_facecolor('#0d1e36')

            model_names = [r['name'] for r in results]
            metrics = ['accuracy', 'precision', 'recall', 'f1']
            x = np.arange(len(model_names))
            width = 0.18
            colors = ['#00e5ff', '#7c4dff', '#ff6b8b', '#00e676']

            for i, metric in enumerate(metrics):
                values = [r[metric] for r in results]
                ax.bar(x + i * width, values, width,
                       label=metric.upper(), color=colors[i],
                       alpha=0.88, edgecolor='none')

            ax.set_xlabel('Model', color='white', fontsize=12,
                          fontweight='bold')
            ax.set_ylabel('Score (%)', color='white', fontsize=12,
                          fontweight='bold')
            ax.set_title('Model Performance Comparison', color='white',
                         fontsize=16, fontweight='bold', pad=15)
            ax.set_xticks(x + width * 1.5)
            ax.set_xticklabels(model_names, color='white', fontsize=10)
            ax.tick_params(axis='y', colors='white')
            ax.legend(loc='lower right', fontsize=9,
                      facecolor='#0d1e36',
                      edgecolor=(1.0, 1.0, 1.0, 0.2),
                      labelcolor='white')
            ax.set_ylim(0, 110)
            ax.grid(axis='y', alpha=0.12, color='white')
            for spine in ('top', 'right'):
                ax.spines[spine].set_visible(False)
            for spine in ('left', 'bottom'):
                ax.spines[spine].set_color((1.0, 1.0, 1.0, 0.2))

            chart = fig_to_base64(fig)

            # ---- Chart 2: Confusion matrix (Random Forest) ----
            y_pred_rf = rf_model.predict(X_test)
            cm = confusion_matrix(y_test, y_pred_rf)

            fig2, ax2 = plt.subplots(figsize=(8, 6))
            fig2.patch.set_facecolor('#0a1628')

            class_names = le.classes_
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=class_names,
                        yticklabels=class_names,
                        ax=ax2, linewidths=0.5,
                        linecolor='#0a1628')
            ax2.set_xlabel('Predicted', color='white', fontsize=12,
                           fontweight='bold')
            ax2.set_ylabel('Actual', color='white', fontsize=12,
                           fontweight='bold')
            ax2.set_title('Random Forest — Confusion Matrix',
                          color='white', fontsize=14, fontweight='bold')
            ax2.tick_params(colors='white')
            plt.setp(ax2.get_xticklabels(), color='white')
            plt.setp(ax2.get_yticklabels(), color='white')

            cm_chart = fig_to_base64(fig2)

            context = {
                'results': results,
                'chart': chart,
                'cm_chart': cm_chart,
                'best_model': best_model_name,
                'best_accuracy': round(best_acc * 100, 2),
                'train_size': len(X_train),
                'test_size': len(X_test),
                'trained': True,
            }
            return render(request, 'users/UserTraining.html', context)

        except Exception as e:
            import traceback
            traceback.print_exc()
            messages.error(request, f'Training error: {str(e)}')

    return render(request, 'users/UserTraining.html', {'trained': False})


# ============================================================
# PREDICTION VIEW
# ============================================================

def UserPrediction(request):
    if 'id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard')
        return redirect('UserLogin')

    prediction_result = None
    input_values = {}

    if request.method == 'POST':
        try:
            import joblib

            model_path = get_model_path()
            if not os.path.exists(model_path):
                messages.warning(
                    request,
                    'No trained model found. Please train the model first.')
                return redirect('UserTraining')

            model_package = joblib.load(model_path)
            model = model_package['model']
            scaler = model_package['scaler']
            le = model_package['label_encoder']
            feature_cols = model_package['feature_columns']

            # Collect input values
            input_dict = {}
            for col in feature_cols:
                raw_val = request.POST.get(col, '').strip()
                try:
                    val = float(raw_val)
                except (ValueError, TypeError):
                    val = 0.0
                input_values[col] = val
                input_dict[col] = [val]

            # Scale & predict using DataFrame (preserves feature names for StandardScaler)
            input_df = pd.DataFrame(input_dict)
            input_scaled = scaler.transform(input_df)
            prediction = model.predict(input_scaled)
            predicted_label = le.inverse_transform(prediction)[0]

            # Confidence (probability)
            confidence = None
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(input_scaled)[0]
                confidence = round(max(proba) * 100, 1)
                class_probs = {
                    le.inverse_transform([i])[0]: round(p * 100, 1)
                    for i, p in enumerate(proba)
                }
            else:
                class_probs = {}

            prediction_result = {
                'label': predicted_label,
                'confidence': confidence,
                'class_probs': class_probs,
            }

        except FileNotFoundError:
            messages.warning(
                request,
                'No trained model found. Please train the model first.')
            return redirect('UserTraining')
        except Exception as e:
            messages.error(request, f'Prediction error: {str(e)}')

    # Build feature fields for the form
    feature_fields = []
    for col in FEATURE_COLUMNS:
        feature_fields.append({
            'name': col,
            'label': FEATURE_LABELS.get(col, col),
            'value': input_values.get(col, ''),
        })

    context = {
        'feature_fields': feature_fields,
        'prediction': prediction_result,
    }
    return render(request, 'users/UserPrediction.html', context)


# ============================================================
# EDA VIEW
# ============================================================

def UserEDA(request):
    if 'id' not in request.session:
        messages.warning(request, 'Please login to access the dashboard')
        return redirect('UserLogin')

    try:
        df = pd.read_csv(get_data_path())
        charts = []

        # ---- 1. Class Distribution ----
        fig, ax = plt.subplots(figsize=(8, 5))
        fig.patch.set_facecolor('#0a1628')
        ax.set_facecolor('#0d1e36')

        class_order = ['Beginner', 'Developing', 'Mature', 'Advanced']
        existing_order = [c for c in class_order if c in df['rdt_level'].unique()]
        class_counts = df['rdt_level'].value_counts().reindex(existing_order)
        bar_colors = ['#ff6b8b', '#ffc107', '#00e676', '#00e5ff']

        bars = ax.bar(class_counts.index, class_counts.values,
                      color=bar_colors[:len(class_counts)],
                      edgecolor='none', alpha=0.88)
        for bar, val in zip(bars, class_counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2.,
                    bar.get_height() + 8,
                    str(val), ha='center', va='bottom',
                    color='white', fontweight='bold', fontsize=12)

        ax.set_title('RDT Level Class Distribution',
                     color='white', fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel('RDT Level', color='white', fontsize=12)
        ax.set_ylabel('Count', color='white', fontsize=12)
        ax.tick_params(colors='white')
        ax.grid(axis='y', alpha=0.12, color='white')
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        for s in ('left', 'bottom'):
            ax.spines[s].set_color((1.0, 1.0, 1.0, 0.2))

        charts.append({
            'title': 'Class Distribution',
            'desc': 'Distribution of Rural Digital Transformation levels '
                    'across all county records.',
            'img': fig_to_base64(fig),
        })

        # ---- 2. Correlation Heatmap ----
        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_facecolor('#0a1628')

        corr = df[FEATURE_COLUMNS].corr()
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f',
                    cmap='coolwarm', ax=ax,
                    linewidths=0.5, linecolor='#0a1628',
                    annot_kws={'size': 7})
        ax.set_title('Feature Correlation Heatmap',
                     color='white', fontsize=16, fontweight='bold', pad=15)
        ax.tick_params(colors='white', labelsize=8)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right',
                 color='white')
        plt.setp(ax.get_yticklabels(), color='white')

        charts.append({
            'title': 'Correlation Heatmap',
            'desc': 'Pearson correlation coefficients between all '
                    'digital transformation features.',
            'img': fig_to_base64(fig),
        })

        # ---- 3. Feature Distribution Grid (top 8 features) ----
        top_features = FEATURE_COLUMNS[:8]
        fig, axes = plt.subplots(2, 4, figsize=(18, 8))
        fig.patch.set_facecolor('#0a1628')

        for feat, ax in zip(top_features, axes.flatten()):
            ax.set_facecolor('#0d1e36')
            ax.hist(df[feat], bins=30, color='#00e5ff',
                    alpha=0.72, edgecolor='none')
            short = FEATURE_LABELS.get(feat, feat)[:25]
            ax.set_title(short, color='white', fontsize=9,
                         fontweight='bold')
            ax.tick_params(colors='white', labelsize=7)
            for s in ('top', 'right'):
                ax.spines[s].set_visible(False)
            for s in ('left', 'bottom'):
                ax.spines[s].set_color((1.0, 1.0, 1.0, 0.2))

        fig.suptitle('Feature Distributions', color='white',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        charts.append({
            'title': 'Feature Distributions',
            'desc': 'Histogram distributions of the top 8 digital '
                    'infrastructure and socioeconomic features.',
            'img': fig_to_base64(fig),
        })

        # ---- 4. Box plots by RDT level ----
        top6 = [
            'broadband_penetration_pct', 'digital_economy_index',
            'ecommerce_turnover_per_capita', 'disposable_income_per_capita',
            'education_years', 'e_participation_index',
        ]
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))
        fig.patch.set_facecolor('#0a1628')

        palette = {
            'Beginner': '#ff6b8b', 'Developing': '#ffc107',
            'Mature': '#00e676', 'Advanced': '#00e5ff',
        }

        for feat, ax in zip(top6, axes.flatten()):
            ax.set_facecolor('#0d1e36')
            sns.boxplot(data=df, x='rdt_level', y=feat, hue='rdt_level', legend=False, ax=ax,
                        order=existing_order, palette=palette,
                        fliersize=3, linewidth=0.8)
            ax.set_title(FEATURE_LABELS.get(feat, feat)[:30],
                         color='white', fontsize=10, fontweight='bold')
            ax.set_xlabel('')
            ax.set_ylabel('')
            ax.tick_params(colors='white', labelsize=8)
            for s in ('top', 'right'):
                ax.spines[s].set_visible(False)
            for s in ('left', 'bottom'):
                ax.spines[s].set_color((1.0, 1.0, 1.0, 0.2))

        fig.suptitle('Feature Comparison by RDT Level', color='white',
                     fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()

        charts.append({
            'title': 'Feature Comparison by RDT Level',
            'desc': 'Box plot comparison of key features across '
                    'different Rural Digital Transformation levels.',
            'img': fig_to_base64(fig),
        })

        # Dataset statistics
        stats = {
            'total_records': len(df),
            'total_features': len(FEATURE_COLUMNS),
            'target_classes': df['rdt_level'].nunique(),
            'class_names': ', '.join(existing_order),
        }

        context = {
            'charts': charts,
            'stats': stats,
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f'EDA error: {str(e)}')
        context = {}

    return render(request, 'users/UserEDA.html', context)
