

import React, { useRef, useEffect, useState } from "react";

interface LineChartProps {
  data: { label: string; value: number }[];
}

export const LineChart: React.FC<LineChartProps> = ({ data }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [animationProgress, setAnimationProgress] = useState(0); // 动画进度
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const maxValue = Math.max(...data.map((item) => item.value));
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;
    const padding = 50;
    const chartWidth = canvasWidth - padding * 2;
    const chartHeight = canvasHeight - padding * 2;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // 绘制背景网格线
    ctx.strokeStyle = "#333";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    for (let i = 0; i <= 10; i++) {
      const y = padding + (chartHeight / 10) * i;
      ctx.moveTo(padding, y);
      ctx.lineTo(canvasWidth - padding, y);
    }
    for (let i = 0; i <= data.length - 1; i++) {
      const x = padding + (chartWidth / (data.length - 1)) * i;
      ctx.moveTo(x, padding);
      ctx.lineTo(x, canvasHeight - padding);
    }
    ctx.stroke();

    // 绘制折线图
    const stepX = chartWidth / (data.length - 1);
    const gradient = ctx.createLinearGradient(padding, 0, canvasWidth - padding, 0);
    gradient.addColorStop(0, "cyan");
    gradient.addColorStop(1, "magenta");

    ctx.strokeStyle = gradient;
    ctx.lineWidth = 2;
    ctx.beginPath();

    data.forEach((item, index) => {
      const x = padding + stepX * index;
      const y = canvasHeight - padding - (item.value / maxValue) * chartHeight;

      if (index === 0) {
        ctx.moveTo(x, y);
      } else {
        const previousX = padding + stepX * (index - 1);
        const previousY =
          canvasHeight - padding - (data[index - 1].value / maxValue) * chartHeight;

        // 动画过渡
        const progressX = previousX + (x - previousX) * animationProgress;
        const progressY = previousY + (y - previousY) * animationProgress;

        ctx.lineTo(progressX, progressY);
      }
    });

    ctx.stroke();

    // 绘制数据点
    data.forEach((item, index) => {
      const x = padding + stepX * index;
      const y = canvasHeight - padding - (item.value / maxValue) * chartHeight;

      ctx.beginPath();
      ctx.arc(x, y, hoverIndex === index ? 6 : 4, 0, Math.PI * 2);
      ctx.fillStyle = hoverIndex === index ? "yellow" : "white";
      ctx.fill();

      // 显示悬停数据值
      if (hoverIndex === index) {
        ctx.fillStyle = "yellow";
        ctx.font = "12px Arial";
        ctx.textAlign = "center";
        ctx.fillText(`Value: ${item.value}`, x, y - 10);
      }
    });

    // 绘制底部标签
    ctx.fillStyle = "white";
    ctx.font = "12px Arial";
    data.forEach((item, index) => {
      const x = padding + stepX * index;
      ctx.fillText(item.label, x, canvasHeight - padding + 20);
    });
  }, [data, animationProgress, hoverIndex]);

  // 动画控制
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationProgress((prev) => Math.min(prev + 0.02, 1));
    }, 16);

    return () => clearInterval(interval);
  }, []);

  // 鼠标悬停处理
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const stepX = (canvas.width - 100) / (data.length - 1);

    const index = Math.round((x - 50) / stepX);
    if (index >= 0 && index < data.length) {
      setHoverIndex(index);
    } else {
      setHoverIndex(null);
    }
  };

  return (
    <canvas
      ref={canvasRef}
      width={600}
      height={400}
      style={{ background: "black", borderRadius: "10px" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setHoverIndex(null)}
    />
  );
};
