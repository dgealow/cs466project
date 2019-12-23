echo 'Greedy, loss 0.1'
for i in {1..20}; do
    python two_state_conflict_matrix.py data/flip/m50_n50_s${i}_k1_loss0.1_a0.001_b0.2.B
done

echo 'Greedy, loss 0.2'
for i in {1..20}; do
    python two_state_conflict_matrix.py data/flip/m50_n50_s${i}_k1_loss0.2_a0.001_b0.2.B
done

echo 'Greedy, loss 0.4'
for i in {1..20}; do
    python two_state_conflict_matrix.py data/flip/m50_n50_s${i}_k1_loss0.4_a0.001_b0.2.B
done
