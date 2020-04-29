% Always put data/constants at first, even thought they are hard coded. 
% ------------ Data input ------------
% Ground truth
X_TRUE = [0,      0.25,   0.5,    0.75,   1,      1.25,   1.5,    1.75];
Y_TRUE = [1.4,    1.4,    1.4,    1.4,    1.4,    1.4,    1.4,    1.4,];
BUFFER_POS = [-0.10, 1.3, 1.95, 0.2];
BLOCKAGE_POS = [0.7, 0.65, 0.6, 0.02];

% Anchor position for geo_1
x_anch = [0,  1,  2,  0,      2];
y_anch = [0,  0,  0,  2.8,    2.8];
% Anchor position for geo_2, one additional anchor in red
x_anch_addition = [1];
y_anch_addition = [0.7];

%5 anchors data Slide 18
x_geo1 = [-0.033, 0.280,  0.297,  0.778,  1.093,  1.367,  1.64,   1.95];
y_geo1 = [1.344,  1.412,  1.416,  1.552,  1.491,  1.576,  1.59,   1.56];
x_geo1_std = [0.087,  0.038,  0.038,  0.030,  0.026,  0.018,  0.025,  0.029];
y_geo1_std = [0.028,  0.017,  0.017,  0.021,  0.015,  0.010,  0.014,  0.013];

%6 anchors, one additional to compensate the blocking vehicle
x_geo2 = [0.061,  0.432,  0.653,  0.946,  1.064,  1.296,  1.656,  1.75];
y_geo2 = [1.47,   1.47,   1.41,   1.434,  1.418,  1.490,  1.510,  1.513];
x_geo2_std = [0.028,  0.041,  0.047,  0.036,  0.019,  0.037,  0.028,  0.025];
y_geo2_std = [0.015,  0.021,  0.028,  0.026,  0.013,  0.014,  0.013,  0.012];

% ------------ Plotting ------------
% Experiment 1, 5 anchors
figure(1);
subplot(1,2,1);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
hold on;
% Plot the dummy handles for legend
std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');

% Plot the std. deviation for all data points of geo1
for i = 1:1:8
    theta = 0 : 0.01 : 2*pi;
    xcenter = x_geo1(i);
    ycenter = y_geo1(i);
    xradius = x_geo1_std(i);
    yradius = y_geo1_std(i);
    x_s = xradius * cos(theta) + xcenter;
    y_s = yradius * sin(theta) + ycenter;
    h = fill(x_s,y_s,'b','facealpha',0.3);
    hold on
end

% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_geo1(i)-X_TRUE(i), y_geo1(i)-Y_TRUE(i),'color','r');
    hold on
end
% Plot the anchor positions
anch = plot(x_anch,y_anch,'b^');
% Plot the buffer (+-10cm) for decawave
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1);
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*');
% Plot the measured positions of tags
measured_1 = plot(x_geo1,y_geo1,'.b');
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos,measured_1,std_1,anch,buff, block],...
    'True Position','Measured Position','Standard Deviation (Oval)',...
    'Anchor', 'Accuracy Buffer (±0.1m)', 'Blockage');
set(l, 'Location', 'north');
title('Size Blockage NLOS Conditions, 5 Fixed Anchors');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% Experiment 2, 6 anchors
subplot(1,2,2);
hold on;
% Plot the dummy handles for legend
std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');
%Plot the std. deviation for all data points of geo2
for i = 1:1:8
    theta = 0 : 0.01 : 2*pi;
    xcenter = x_geo2(i);
    ycenter = y_geo2(i);
    xradius = x_geo2_std(i);
    yradius = y_geo2_std(i);
    x_s = xradius * cos(theta) + xcenter;
    y_s = yradius * sin(theta) + ycenter;
    h = fill(x_s,y_s,'b','facealpha',0.3);
    hold on
end
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_geo2(i)-X_TRUE(i), y_geo2(i)-Y_TRUE(i),'color','r');
    hold on
end
anch = plot(x_anch,y_anch,'b^');
anch_add = plot(x_anch_addition, y_anch_addition,'r^');
% Plot the buffer (+-10cm) for decawave
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1);
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*');
% Plot the measured positions of tags
measured_2 = plot(x_geo2,y_geo2,'.b');
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos, measured_2, std_1, anch, anch_add, buff, block],...
    'True Position','Measured Position','Standard Deviation (Oval)',...
    'Original Anchors', 'Added Anchor', 'Accuracy Buffer (±0.1m)', 'Blocakge');
set(l, 'Location', 'north');
title('Size Blockage NLOS Conditions, 5 Fixed Anchors and 1 Relaying Anchor');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;


% Zoom in, plot error bar only, no anchors
figure(2);
subplot(2,1,1);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
e1 = errorbar(x_geo1, y_geo1, y_geo1_std, y_geo1_std, x_geo1_std, x_geo1_std,...
    'Marker','o');
hold on;
% Plot the dummy handles for legend
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
% replot in a zoomed-in manner
rectangle('Position',RECTANGLE_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1);
true_pos = plot(X_TRUE,Y_TRUE,'r*');
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_geo1(i)-X_TRUE(i), y_geo1(i)-Y_TRUE(i),'color','r');
    hold on
end
daspect([1 1 1]);
grid on;
l = legend([true_pos,e1,buff],'True Position','Measured Position','Accuracy Buffer (±0.1m)');
set(l, 'Location', 'northeast');
axis([-0.5 2.5 1.2 1.7]);
title('Size Blockage NLOS Conditions, 5 Fixed Anchors (Zoomed in)');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

subplot(2,1,2);
e2 = errorbar(x_geo2, y_geo2, y_geo2_std, y_geo2_std, x_geo2_std, x_geo2_std,...
    'Marker','o');
hold on;
% Plot the dummy handles for legend
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
% replot in a zoomed-in manner
rectangle('Position',RECTANGLE_POS, 'LineStyle','--', 'EdgeColor','m','Curvature', 1);
true_pos = plot(X_TRUE,Y_TRUE,'r*');
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_geo2(i)-X_TRUE(i), y_geo2(i)-Y_TRUE(i),'color','r');
    hold on
end
daspect([1 1 1]);
grid on;
l = legend([true_pos,e2,buff],'True Position','Measured Position','Accuracy Buffer (±0.1m)');
set(l, 'Location', 'northeast');
axis([-0.5 2.5 1.2 1.7]);
title('Size Blockage NLOS Conditions, 5 Fixed Anchors and 1 Relaying Anchor (Zoomed in)');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

