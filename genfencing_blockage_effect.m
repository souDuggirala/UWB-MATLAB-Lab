% ------------ Data input ------------
X_SCALE = 1/8;          % the X scale ratio used for this miniature experiment
Y_SCALE = 1/8;          % the Y scale ratio used for this miniature experiment
ACCURACY_BUFFER = 0.1;  % accuracy buffer provided by Decawave

% Position of metal blockage (rectangular shape) used in the experiment
% Four-element vector of the form [x y w h]: 
% x, y of lower-left corner;
% w, h - width and height of the rectangle
BLOCKAGE_POS = [0.7, 0.65, 0.6, 0.02];

% Ground truth values of tag positions, X and Y
Y_TAG = 1.4;    % all the tags have the same ground truth Y value
X_TRUE = [0,      0.25,   0.5,    0.75,   1,      1.25,   1.5,    1.75];
Y_TRUE = repelem(Y_TAG, 8);


% factual buffer position, unscaled
BUFFER_POS = [
    min(X_TRUE) - ACCURACY_BUFFER, ...
    min(Y_TRUE) - ACCURACY_BUFFER, ...
    min(X_TRUE) - ACCURACY_BUFFER + (max(X_TRUE) - min(X_TRUE)) + ACCURACY_BUFFER*3, ...
    2 * ACCURACY_BUFFER];
% scaled buffer position, rectangle
% Four-element vector of the form [x y w h]: 
% x, y of lower-left corner;
% w, h - width and height of the rectangle
BUFFER_POS_scaled = [
    min(X_TRUE) - ACCURACY_BUFFER*X_SCALE, ...
    min(Y_TRUE) - ACCURACY_BUFFER*Y_SCALE, ...
    min(X_TRUE) - ACCURACY_BUFFER*X_SCALE + (max(X_TRUE) - min(X_TRUE)) + ACCURACY_BUFFER*X_SCALE*3, ...
    2 * ACCURACY_BUFFER*Y_SCALE];

% measured positions of tags with 5 anchors: experiment 1
x_exp1 = [-0.033, 0.280,  0.297,  0.778,  1.093,  1.367,  1.64,   1.95];
y_exp1 = [1.344,  1.412,  1.416,  1.552,  1.491,  1.576,  1.59,   1.56];
x_exp1_std = [0.087,  0.038,  0.038,  0.030,  0.026,  0.018,  0.025,  0.029];
y_exp1_std = [0.028,  0.017,  0.017,  0.021,  0.015,  0.010,  0.014,  0.013];

% measured positions of tags with 6 anchors: experiment 2
% experiment 2: added one additional anchor to compensate the blockage
% TODO: implement a datapreprocessing pipeline to avoid hard coded data
x_exp2 = [0.061,  0.432,  0.653,  0.946,  1.064,  1.296,  1.656,  1.75];
y_exp2 = [1.47,   1.47,   1.41,   1.434,  1.418,  1.490,  1.510,  1.513];
x_exp2_std = [0.028,  0.041,  0.047,  0.036,  0.019,  0.037,  0.028,  0.025];
y_exp2_std = [0.015,  0.021,  0.028,  0.026,  0.013,  0.014,  0.013,  0.012];

% Calculate the scaled value for measured Y values of both experiments
y_exp1_scaled_delta = (Y_TRUE - y_exp1)*Y_SCALE + Y_TRUE;
y_exp2_scaled_delta = (Y_TRUE - y_exp2)*Y_SCALE + Y_TRUE;
% Anchor position for experiment 1
X_ANCH = [0,  1,  2,  0,      2];
Y_ANCH = [0,  0,  0,  2.8,    2.8];
% Anchor position for experiment 2, one additional anchor in red
X_ANCH_ADDITIONAL = [1];
Y_ANCH_ADDITIONAL = [0.7];

% ------------ Plotting ------------
% Experiment 1, 5 anchors
figure(1);
subplot(1,2,1);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
hold on;
% Plot the dummy handles for the legend
std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
buff = plot(nan, nan, 'LineStyle','-.', 'Color',[.61 .51 .74]); % purple
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');

% Plot the std. deviation for all data points of experiment 1
for i = 1:1:8
    theta = 0 : 0.01 : 2*pi;
    xcenter = x_exp1(i);
    ycenter = y_exp1(i);
    xradius = x_exp1_std(i);
    yradius = y_exp1_std(i);
    x_s = xradius * cos(theta) + xcenter;
    y_s = yradius * sin(theta) + ycenter;
    h = fill(x_s,y_s,'b','facealpha',0.3);
    hold on
end

% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_exp1(i)-X_TRUE(i), y_exp1(i)-Y_TRUE(i),...
        'color','k','LineStyle',':','LineWidth',0.3);
    hold on
end
% Plot the anchor positions
anch = plot(X_ANCH,Y_ANCH,'b^');
% Plot the buffer (+-10cm) for decawave
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1,'LineWidth',0.3);
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
% Plot the measured positions of tags
measured_1 = plot(x_exp1,y_exp1,'b.-.','LineWidth',1);
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos,measured_1,std_1,anch,buff, block],...
    'True Position','Measured Position','Standard Deviation (Oval)',...
    'Anchor', 'Accuracy Buffer (±0.1m)', 'Blockage');
set(l, 'Location', 'north');
title('Side Blockage NLOS Conditions, 5 Fixed Anchors');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% ------------ Plotting ------------
% Experiment 2, 6 anchors
subplot(1,2,2);
hold on;
% Plot the dummy handles for legend
std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
buff = plot(nan, nan, 'LineStyle','-.', 'Color',[.61 .51 .74]); % makes purple;
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');
%Plot the std. deviation for all data points of experiment 2
for i = 1:1:8
    theta = 0 : 0.01 : 2*pi;
    xcenter = x_exp2(i);
    ycenter = y_exp2(i);
    xradius = x_exp2_std(i);
    yradius = y_exp2_std(i);
    x_s = xradius * cos(theta) + xcenter;
    y_s = yradius * sin(theta) + ycenter;
    h = fill(x_s,y_s,'b','facealpha',0.3);
    hold on
end
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_exp2(i)-X_TRUE(i), y_exp2(i)-Y_TRUE(i),...
        'color','k','LineStyle',':','LineWidth',0.3);
    hold on
end
anch = plot(X_ANCH,Y_ANCH,'b^');
anch_add = plot(X_ANCH_ADDITIONAL, Y_ANCH_ADDITIONAL,'r^');
% Plot the buffer (+-10cm) for decawave
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1,'LineWidth',0.3);
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
% Plot the measured positions of tags
measured_2 = plot(x_exp2,y_exp2,'b.-.','LineWidth',1);
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos, measured_2, std_1, anch, anch_add, buff, block],...
    'True Position','Measured Position','Standard Deviation (Oval)',...
    'Original Anchors', 'Added Anchor', 'Accuracy Buffer (±0.1m)', 'Blockage');
set(l, 'Location', 'north');
title('Side Blockage NLOS Conditions, 5 Fixed Anchors and 1 Relaying Anchor');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% ------------ Plotting ------------
% Experiment 1 Zoom in, plot error bar only, no anchors (outside the scope)
figure(2);
subplot(2,1,1);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
hold on;
% Plot the dummy handles for legend
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
% replot in a zoomed-in manner
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m', 'Curvature', 1,'LineWidth',0.3);
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
e1 = errorbar(x_exp1, y_exp1, y_exp1_std, y_exp1_std, x_exp1_std, x_exp1_std,...
    'Marker','o','LineStyle','-','LineWidth',1, 'Color', 'b');
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_exp1(i)-X_TRUE(i), y_exp1(i)-Y_TRUE(i),...
        'LineStyle',':','LineWidth',0.3,'Color','k');
    hold on
end
daspect([1 1 1]);
grid on;
l = legend([true_pos,e1,buff],'True Position','Measured Position','Accuracy Buffer (±0.1m)');
set(l, 'Location', 'northeast');
axis([-0.5 2.5 1.2 1.7]);
title('Side Blockage NLOS Conditions, 5 Fixed Anchors (Zoomed in)');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% ------------ Plotting ------------
% Experiment 2 Zoom in, plot error bar only, no anchors (outside the scope)
subplot(2,1,2);
hold on;
% Plot the dummy handles for legend
buff = plot(nan, nan, 'LineStyle','--', 'Color','m');
% replot in a zoomed-in manner
rectangle('Position',BUFFER_POS, 'LineStyle','--', 'EdgeColor','m','Curvature', 1);
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
e2 = errorbar(x_exp2, y_exp2, y_exp2_std, y_exp2_std, x_exp2_std, x_exp2_std,...
    'Marker','o','LineStyle','-','LineWidth',1, 'Color', 'b');
% Plot the connection from truth to measurements
for i = 1:1:8
    quiver(X_TRUE(i), Y_TRUE(i), x_exp2(i)-X_TRUE(i), y_exp2(i)-Y_TRUE(i),...
        'color','k','LineStyle',':','LineWidth',0.3);
    hold on
end
daspect([1 1 1]);
grid on;
l = legend([true_pos,e2,buff],'True Position','Measured Position','Accuracy Buffer (±0.1m)');
set(l, 'Location', 'northeast');
axis([-0.5 2.5 1.2 1.7]);
title('Side Blockage NLOS Conditions, 5 Fixed Anchors and 1 Relaying Anchor (Zoomed in)');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% ------------ Plotting ------------
% Plot scaled values for experiment 1, no zoom in, no buffer zone
figure(3);
subplot(1,2,1);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
hold on;
% Plot the dummy handles for legend
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');
% Plot the anchor positions
anch = plot(X_ANCH,Y_ANCH,'b^');
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
% Plot the measured positions of tags
scaled_1 = plot(x_exp1,y_exp1_scaled_delta,'b.-.','LineWidth',1);
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos,scaled_1,anch, block],...
    'True Position','Measured Position (Scaled Y)',...
    'Anchor', 'Blockage');
set(l, 'Location', 'north');
title('Side Blockage NLOS Conditions, 5 Fixed Anchors, Scaled Y');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;

% ------------ Plotting ------------
% Plot scaled values for experiment 2, no zoom in, no buffer zone
subplot(1,2,2);
set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
hold on;
% Plot the dummy handles for legend
block = plot(nan, nan, 'ks', 'MarkerFaceColor','k');
% Plot the additional anchor
anch = plot(X_ANCH,Y_ANCH,'b^');
anch_add = plot(X_ANCH_ADDITIONAL, Y_ANCH_ADDITIONAL,'r^');
% Plot the blockage
rectangle('Position',BLOCKAGE_POS, 'EdgeColor','k', 'FaceColor', 'k', 'Curvature', 0.2,'LineWidth',0.3);
% Plot the true positions of tags
true_pos = plot(X_TRUE,Y_TRUE,'r*-','LineWidth',1);
% Plot the measured positions of tags
scaled_2 = plot(x_exp2,y_exp2_scaled_delta,'b.-.','LineWidth',1);
axis([-0.5 2.5 -0.5 3]);
daspect([1 1 1]);
grid on;
l = legend([true_pos, scaled_2, anch, anch_add, block],...
    'True Position','Measured Position (Scaled Y)',...
    'Original Anchors', 'Added Anchor', 'Blockage');
set(l, 'Location', 'north');
title('Side Blockage NLOS Conditions, 5 Fixed Anchors and 1 Relaying Anchor, Scaled Y');
xlabel('X coordinate (m)');
ylabel('Y coordinate (m)');
hold off;