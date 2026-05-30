from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination, BeliefPropagation
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

def build_medical_bayesian_network():
    model = BayesianNetwork([
        ('Smoking', 'LungCancer'),
        ('AirPollution', 'LungCancer'),
        ('LungCancer', 'Cough'),
        ('LungCancer', 'ChestPain'),
        ('LungCancer', 'Dyspnoea'),
        ('Flu', 'Cough'),
        ('Flu', 'Fever'),
        ('AgeRisk', 'LungCancer'),
    ])

    cpd_smoking = TabularCPD(
        variable='Smoking',
        variable_card=2,
        values=[[0.7], [0.3]],
        state_names={'Smoking': ['No', 'Yes']}
    )

    cpd_air = TabularCPD(
        variable='AirPollution',
        variable_card=2,
        values=[[0.6], [0.4]],
        state_names={'AirPollution': ['Low', 'High']}
    )

    cpd_age = TabularCPD(
        variable='AgeRisk',
        variable_card=2,
        values=[[0.65], [0.35]],
        state_names={'AgeRisk': ['Young', 'Old']}
    )

    cpd_flu = TabularCPD(
        variable='Flu',
        variable_card=2,
        values=[[0.85], [0.15]],
        state_names={'Flu': ['No', 'Yes']}
    )

    cpd_cancer = TabularCPD(
        variable='LungCancer',
        variable_card=2,
        values=[
            [0.98, 0.92, 0.94, 0.88, 0.85, 0.78, 0.82, 0.72],
            [0.02, 0.08, 0.06, 0.12, 0.15, 0.22, 0.18, 0.28],
        ],
        evidence=['Smoking', 'AirPollution', 'AgeRisk'],
        evidence_card=[2, 2, 2],
        state_names={
            'LungCancer': ['No', 'Yes'],
            'Smoking': ['No', 'Yes'],
            'AirPollution': ['Low', 'High'],
            'AgeRisk': ['Young', 'Old'],
        }
    )

    cpd_cough = TabularCPD(
        variable='Cough',
        variable_card=2,
        values=[
            [0.95, 0.60, 0.70, 0.30],
            [0.05, 0.40, 0.30, 0.70],
        ],
        evidence=['LungCancer', 'Flu'],
        evidence_card=[2, 2],
        state_names={
            'Cough': ['No', 'Yes'],
            'LungCancer': ['No', 'Yes'],
            'Flu': ['No', 'Yes'],
        }
    )

    cpd_chest = TabularCPD(
        variable='ChestPain',
        variable_card=2,
        values=[
            [0.92, 0.35],
            [0.08, 0.65],
        ],
        evidence=['LungCancer'],
        evidence_card=[2],
        state_names={
            'ChestPain': ['No', 'Yes'],
            'LungCancer': ['No', 'Yes'],
        }
    )

    cpd_dyspnoea = TabularCPD(
        variable='Dyspnoea',
        variable_card=2,
        values=[
            [0.90, 0.40],
            [0.10, 0.60],
        ],
        evidence=['LungCancer'],
        evidence_card=[2],
        state_names={
            'Dyspnoea': ['No', 'Yes'],
            'LungCancer': ['No', 'Yes'],
        }
    )

    cpd_fever = TabularCPD(
        variable='Fever',
        variable_card=2,
        values=[
            [0.97, 0.45],
            [0.03, 0.55],
        ],
        evidence=['Flu'],
        evidence_card=[2],
        state_names={
            'Fever': ['No', 'Yes'],
            'Flu': ['No', 'Yes'],
        }
    )

    model.add_cpds(
        cpd_smoking, cpd_air, cpd_age, cpd_flu,
        cpd_cancer, cpd_cough, cpd_chest, cpd_dyspnoea, cpd_fever
    )

    assert model.check_model(), "Model is invalid!"
    return model


def run_inference(model):
    infer = VariableElimination(model)

    print("\n" + "="*60)
    print("  BAYESIAN NETWORK INFERENCE - MEDICAL DIAGNOSIS")
    print("="*60)

    prior = infer.query(['LungCancer'])
    print("\nPrior probability of Lung Cancer:")
    for state, prob in zip(prior.state_names['LungCancer'], prior.values):
        print(f"  P(LungCancer={state}) = {prob:.4f}")

    evidence1 = {'Smoking': 'Yes', 'AgeRisk': 'Old'}
    result1 = infer.query(['LungCancer'], evidence=evidence1)
    print("\nP(LungCancer | Smoking=Yes, AgeRisk=Old):")
    for state, prob in zip(result1.state_names['LungCancer'], result1.values):
        print(f"  P(LungCancer={state}) = {prob:.4f}")

    evidence2 = {'Cough': 'Yes', 'ChestPain': 'Yes', 'Dyspnoea': 'Yes'}
    result2 = infer.query(['LungCancer'], evidence=evidence2)
    print("\nP(LungCancer | Cough=Yes, ChestPain=Yes, Dyspnoea=Yes):")
    for state, prob in zip(result2.state_names['LungCancer'], result2.values):
        print(f"  P(LungCancer={state}) = {prob:.4f}")

    evidence3 = {'Cough': 'Yes', 'Fever': 'Yes'}
    result3 = infer.query(['LungCancer', 'Flu'], evidence=evidence3)
    print("\nP(LungCancer | Cough=Yes, Fever=Yes) - could be Flu:")
    for state, prob in zip(result3.state_names['LungCancer'], result3.values[:, 0]):
        print(f"  P(LungCancer={state}) = {prob:.4f}")

    evidence4 = {'Smoking': 'Yes', 'AirPollution': 'High', 'AgeRisk': 'Old', 'Cough': 'Yes', 'ChestPain': 'Yes'}
    result4 = infer.query(['LungCancer'], evidence=evidence4)
    print("\nP(LungCancer | Smoking=Yes, AirPollution=High, AgeRisk=Old, Cough=Yes, ChestPain=Yes):")
    for state, prob in zip(result4.state_names['LungCancer'], result4.values):
        print(f"  P(LungCancer={state}) = {prob:.4f}")

    evidence5 = {'LungCancer': 'Yes'}
    result_cough = infer.query(['Cough'], evidence=evidence5)
    result_chest = infer.query(['ChestPain'], evidence=evidence5)
    result_dysp = infer.query(['Dyspnoea'], evidence=evidence5)
    print("\nSymptom probabilities given LungCancer=Yes:")
    for state, prob in zip(result_cough.state_names['Cough'], result_cough.values):
        print(f"  P(Cough={state} | Cancer) = {prob:.4f}")
    for state, prob in zip(result_chest.state_names['ChestPain'], result_chest.values):
        print(f"  P(ChestPain={state} | Cancer) = {prob:.4f}")
    for state, prob in zip(result_dysp.state_names['Dyspnoea'], result_dysp.values):
        print(f"  P(Dyspnoea={state} | Cancer) = {prob:.4f}")

    return infer


def visualize_bn(model, output_path="bayesian_network.png"):
    G = nx.DiGraph()
    G.add_edges_from(model.edges())

    node_colors = {
        'Smoking': '#FF8A65',
        'AirPollution': '#FF8A65',
        'AgeRisk': '#FF8A65',
        'Flu': '#FF8A65',
        'LungCancer': '#EF5350',
        'Cough': '#81C784',
        'ChestPain': '#81C784',
        'Dyspnoea': '#81C784',
        'Fever': '#81C784',
    }

    colors = [node_colors.get(n, '#90CAF9') for n in G.nodes()]

    plt.figure(figsize=(12, 8))
    pos = {
        'Smoking': (0, 3),
        'AirPollution': (2, 3),
        'AgeRisk': (4, 3),
        'Flu': (6, 3),
        'LungCancer': (2, 1.5),
        'Cough': (0, 0),
        'ChestPain': (2, 0),
        'Dyspnoea': (4, 0),
        'Fever': (6, 0),
    }

    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=2500, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='#555555', arrows=True,
                           arrowsize=25, width=2, connectionstyle='arc3,rad=0.0')

    legend_elements = [
        plt.matplotlib.patches.Patch(facecolor='#FF8A65', label='Risk Factors'),
        plt.matplotlib.patches.Patch(facecolor='#EF5350', label='Disease'),
        plt.matplotlib.patches.Patch(facecolor='#81C784', label='Symptoms'),
    ]
    plt.legend(handles=legend_elements, loc='upper right', fontsize=9)
    plt.title("Bayesian Network: Lung Cancer Diagnosis", fontsize=13, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches='tight')
    plt.close()
    print(f"Bayesian Network diagram saved to: {output_path}")


def sensitivity_analysis(infer):
    print("\n" + "="*60)
    print("  SENSITIVITY ANALYSIS")
    print("="*60)

    scenarios = [
        ("Non-smoker, young, low pollution", {'Smoking': 'No', 'AgeRisk': 'Young', 'AirPollution': 'Low'}),
        ("Smoker, young, low pollution",     {'Smoking': 'Yes', 'AgeRisk': 'Young', 'AirPollution': 'Low'}),
        ("Non-smoker, old, low pollution",   {'Smoking': 'No', 'AgeRisk': 'Old', 'AirPollution': 'Low'}),
        ("Non-smoker, young, high pollution",{'Smoking': 'No', 'AgeRisk': 'Young', 'AirPollution': 'High'}),
        ("Smoker, old, high pollution",      {'Smoking': 'Yes', 'AgeRisk': 'Old', 'AirPollution': 'High'}),
    ]

    print(f"\n{'Scenario':<45} {'P(Cancer=Yes)':>15}")
    print("-"*62)
    for label, evidence in scenarios:
        result = infer.query(['LungCancer'], evidence=evidence)
        cancer_yes_idx = result.state_names['LungCancer'].index('Yes')
        prob = result.values[cancer_yes_idx]
        print(f"{label:<45} {prob:>15.4f}")


model = build_medical_bayesian_network()
print("Bayesian Network Structure:")
print(f"  Nodes : {list(model.nodes())}")
print(f"  Edges : {list(model.edges())}")
print(f"  Valid  : {model.check_model()}")

infer = run_inference(model)
sensitivity_analysis(infer)
visualize_bn(model, "/mnt/user-data/outputs/bayesian_network.png")
