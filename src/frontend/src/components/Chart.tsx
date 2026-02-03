import {
    LineChart,
    Line,
    ResponsiveContainer,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceArea,
} from "recharts";

type ChartProps = {
    values: number[];
};

export default function Chart({ values }: ChartProps) {
    const maxValue = Math.max(...values, 1);
    const chartMax = Math.max(1, Math.ceil(maxValue * 1.1));
    const latest = values[values.length - 1];
    const data = values.map((value, index) => ({ index: index + 1, hours: value }));

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 sm:py-5">
                <div className="mb-3 text-xs text-slate-500">Latest forecast: {latest} hrs</div>
                <div className="h-56 w-full sm:h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data} margin={{ top: 8, right: 20, left: 0, bottom: 8 }}>
                            <CartesianGrid strokeDasharray="4 4" stroke="#e2e8f0" />
                            <XAxis
                                dataKey="index"
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#94a3b8", fontSize: 12 }}
                            />
                            <YAxis
                                domain={[0, chartMax]}
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#94a3b8", fontSize: 12 }}
                                tickFormatter={(value) => `${value}h`}
                            />
                            <ReferenceArea y1={0} y2={24} fill="#fee2e2" fillOpacity={0.55} />
                            <ReferenceArea y1={24} y2={72} fill="#fef3c7" fillOpacity={0.6} />
                            <ReferenceArea y1={72} y2={chartMax} fill="#dcfce7" fillOpacity={0.45} />
                            <Tooltip
                                formatter={(value) => [`${value} hrs`, "Hours to breakdown"]}
                                labelFormatter={(label) => `Reading #${label}`}
                            />
                            <Line
                                type="monotone"
                                dataKey="hours"
                                stroke="#0ea5e9"
                                strokeWidth={3}
                                dot={{ r: 4, fill: "#0ea5e9" }}
                                activeDot={{ r: 6 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
