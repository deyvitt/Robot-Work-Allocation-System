// frontend/app.js
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('allocForm');
    const outputDiv = document.getElementById('output');
    const submitBtn = document.getElementById('submitBtn');
    const levelSelect = document.getElementById('level');
    const hoursInput = document.getElementById('hours_input');
    const hoursHint = document.getElementById('hours-hint');

    // Dynamic hint based on level
    levelSelect.addEventListener('change', () => {
        if (levelSelect.value === '4') {
            hoursInput.placeholder = 'e.g. 12, 16, 21';
            hoursHint.textContent = 'Comma or space separated for multiple clients';
        } else {
            hoursInput.placeholder = 'e.g. 20';
            hoursHint.textContent = 'Single value for Levels 1–3';
        }
    });
    levelSelect.dispatchEvent(new Event('change', { bubbles: true }));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSubmission();
    });

    async function handleSubmission() {
        outputDiv.textContent = '';
        outputDiv.className = 'output-box loading';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Processing...';

        try {
            const level = parseInt(document.getElementById('level').value, 10);
            const bravo = parseInt(document.getElementById('bravo').value, 10);
            const charlie = parseInt(document.getElementById('charlie').value, 10);
            const delta = parseInt(document.getElementById('delta').value, 10);
            const hoursRaw = document.getElementById('hours_input').value.trim();

            if ([level, bravo, charlie, delta].some(isNaN)) throw new Error('All robot counts and level must be valid integers.');
            if (bravo < 0 || charlie < 0 || delta < 0) throw new Error('Robot counts cannot be negative.');
            if (!hoursRaw) throw new Error('Client work hours cannot be empty.');
            if (!/^[\d\s,]+$/.test(hoursRaw)) throw new Error('Hours must contain only numbers, commas, or spaces.');

            const payload = { level, bravo, charlie, delta, hours_input: hoursRaw };
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000);

            const response = await fetch('/api/allocate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (!response.ok) {
                let err = `HTTP ${response.status}: ${response.statusText}`;
                try { const d = await response.json(); if (d?.detail) err = d.detail; } catch {}
                throw new Error(err);
            }

            const data = await response.json();
            if (data.status !== 'success') throw new Error(data.error || 'Unexpected server response.');

            outputDiv.innerHTML = formatOutput(data, level);
            outputDiv.classList.remove('loading');
            outputDiv.classList.add('success');
        } catch (error) {
            let msg = error.message;
            if (error.name === 'AbortError') msg = 'Request timed out. Server may be restarting.';
            outputDiv.innerHTML = `<span class="error">❌ ${escapeHtml(msg)}</span>`;
            outputDiv.classList.remove('loading');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Calculate Allocation';
        }
    }

    function escapeHtml(str) {
        const d = document.createElement('div'); d.textContent = str; return d.innerHTML;
    }

    function formatOutput(data, level) {
        let out = '';
        if (level === 1 && data.allocation) {
            const a = data.allocation;
            if (a.valid === false) return `❌ ${a.error || 'Allocation failed.'}\n`;
            out += `📊 LEVEL 1: Category Distribution Strategy\nRobot Assignment:\n`;
            if (a.bravo > 0) out += `  Bravo: ${a.bravo}\n`;
            if (a.charlie > 0) out += `  Charlie: ${a.charlie}\n`;
            if (a.delta > 0) out += `  Delta: ${a.delta}\n`;
            out += `Total Work Hours Provided: ${a.total_hours}\nClient Work Hours Requested: ${a.requested}\n`;
        } else if (level === 2 && data.level2) {
            const l2 = data.level2;
            if (l2.valid === false) return `❌ ${l2.error || 'Allocation failed.'}\n`;
            out += `💰 LEVEL 2: Cost Optimised Allocation\nCost Optimized Allocation:\n`;
            if (l2.bravo > 0) out += `  Bravo: ${l2.bravo}\n`;
            if (l2.charlie > 0) out += `  Charlie: ${l2.charlie}\n`;
            if (l2.delta > 0) out += `  Delta: ${l2.delta}\n`;
            out += `Total Hours Provided: ${l2.hours}\nTotal Charging Cost: $${l2.cost}\n\n`;
            out += `Level 1 vs Level 2 Comparison\n  Level 1 Cost: $${data.level1_cost}\n  Level 2 Cost: $${data.level2.cost}\n`;
            out += `  Cost Difference: $${data.cost_difference}\n`;
            if (data.insight) out += `  Insight: ${data.insight}\n`;
        } else if (level === 3) {
            out += `🔋 LEVEL 3: Standby Activation Strategy\nActive Robot Capacity: ${data.active_capacity} hours\nClient Work Requested: ${data.requested} hours\n`;
            if (data.deficit > 0 && data.standby) {
                if (data.standby.valid === false) return `❌ ${data.standby.error || 'Standby failed.'}\n`;
                out += `Additional Standby Robots Required:\n`;
                if (data.standby.bravo > 0) out += `  Bravo: ${data.standby.bravo}\n`;
                if (data.standby.charlie > 0) out += `  Charlie: ${data.standby.charlie}\n`;
                if (data.standby.delta > 0) out += `  Delta: ${data.standby.delta}\n`;
                out += `Standby Cost: $${data.standby.cost}\n`;
            } else out += `Sufficient active capacity. No standby robots required.\n`;
        } else if (level === 4 && data.allocations) {
            out += `📈 LEVEL 4: Multi-Client Allocation\n`;
            data.allocations.forEach(c => {
                const icon = c.status === 'allocated' ? '✅' : c.status === 'standby_required' ? '⚠️' : '❌';
                out += `Client ${c.client} (${c.hours}h): ${icon} ${c.status.replace(/_/g, ' ')}\n`;
                if (c.assigned) out += `  ${c.assigned}\n`;
                if (c.standby) out += `  Standby: ${c.standby}\n`;
                if (c.error) out += `  Reason: ${c.error}\n`;
            });
            if (data.summary) {
                out += `\n📊 ALLOCATION SUMMARY\nTotal Robots Used: Bravo=${data.summary.total_robots_used.Bravo}, Charlie=${data.summary.total_robots_used.Charlie}, Delta=${data.summary.total_robots_used.Delta}\n`;
                out += `Total Charging Cost: $${data.summary.total_cost}\nAvg Robot Utilisation: ${data.summary.avg_utilisation}%\n`;
                if (data.summary.efficiency_metrics) {
                    out += `\n📈 EFFICIENCY METRICS\nBravo Utilisation: ${data.summary.efficiency_metrics.Bravo}%\nCharlie Utilisation: ${data.summary.efficiency_metrics.Charlie}%\nDelta Utilisation: ${data.summary.efficiency_metrics.Delta}%\n`;
                }
            }
        } else out = '⚠️ Unexpected response format.';
        return out;
    }
});
