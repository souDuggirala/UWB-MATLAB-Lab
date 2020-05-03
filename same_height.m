%Ground truth
X_TRUE = [0.22:0.29:2.25];
Y_TRUE = repelem([0.55],length(X_TRUE));
BUFFER_POS = [0.12, 0.45, 2.23, 0.2];

%Anchor Positions  for height exp
x_anch_height=[0,0,2.33,2.33];
y_anch_height=[0,1.11,1.11,0];

%Anchor position for exp 4(geo1) slide 18
x_anch_exp4=[0,0,2.33,2.33];
y_anch_exp4=[0,1.11,1.11,0];

%Anchor position for exp 4(geo2) slide 18
x_anch_exp4_geo2=[0,0,2.33,2.33,1];
y_anch_exp4_geo2=[0,1.11,1.11,0,1.11];

%Anchor Positions  for square geometry
x_anch_sqr=[0,0,2.33,2.33];
y_anch_sqr=[0,1.11,1.11,0];

%Anchor Positions  for Triangle geometry
x_anch_tri = [0,1.143,2.33,1.143];
y_anch_tri = [0,0,0,1.168];

%Anchor Positions on one side data(Slide 11)
x_anch_one_side = [0,   0.9,    2.33,   1.8];
y_anch_one_side = [0,   0,      0,      -0.3];

%Anchor position for anchors on one side with two anchors further away Slide 13
x_anch_one_side_far = [0,   0.5,    2.33,   1.8];
y_anch_one_side_far = [0,   -0.3,   0,      -0.3];

%Effect of anchor height(Slide 7) 2nd plot data
x_anch_elevated=[0.19,0.40,0.85,1.02,1.37,1.65,1.98,2.23];
y_anch_elevated=[0.55,0.43,0.61,0.69,0.82,0.22,0.57,0.41];
x_anch_elevated_std=[0.017,0.013,0.009,0.052,0.017,0.018,0.036,0.025];
y_anch_elevated_std=[0.012,0.020,0.027,0.085,0.017,0.015,0.011,0.012];

x_tag_elevated=[0.27,0.58,0.97,1.27,1.50,1.95,2.11,2.38];
y_tag_elevated=[0.42,0.22,0.80,0.49,0.45,0.87,0.67,0.83];
x_tag_elevated_std=[0.019,0.028,0.029,0.009,0.022,0.020,0.017,0.024];
y_tag_elevated_std=[0.018,0.041,0.029,0.020,0.015,0.020,0.013,0.018];


%Exp4 geo1 data(Slide 18)
x_anch_geo1=[0.089,0.428,0.84,0.989,1.345,1.69,1.99,2.45];
y_anch_geo1=[0.268,0.429,0.41,0.026,0.218,0.052,0.506,0.60];
x_anch_geo1_std=[0.030,0.013,0.034,0.035,0.044,0.071,0.012,0.0251];
y_anch_geo1_std=[0.025,0.014,0.089,0.025,0.0257,0.0140,0.029,0.019];

%Exp4 geo2 data(Slide 18)
x_anch_geo2=[0.185,0.621,0.728,1.025,1.341,1.624,1.832,2.289];
y_anch_geo2=[0.281,0.507,0.799,0.717,0.670,0.671,0.528,0.604];
x_anch_geo2_std=[0.043,0.034,0.038,0.013,0.015,0.019,0.016,0.030];
y_anch_geo2_std=[0.0247,0.037,0.044,0.026,0.016,0.021,0.016,0.023];

%Square geometry data(Slide 9)
%x_sqr =     [0.22,  0.53,   0.82,   1.08,   1.39,   1.72,   2.07,   2.50];
%y_sqr =     [0.55,  0.53,   0.56,   0.56,   0.57,   0.68,   0.72,   0.77];
%x_sqr_std = [0.025, 0.024,  0.022,  0.022,  0.025,  0.013,  0.022,  0.038];
%y_sqr_std = [0.016, 0.015,  0.010,  0.009,  0.013,  0.019,  0.026,  0.0291];

%Square geo-2
x_sqr=[0.17,0.50,0.78,1.09,1.34,1.62,1.98,2.44];
y_sqr=[0.59,0.57,0.60,0.59,0.69,0.64,0.62,0.61];
x_sqr_std=[0.029,0.018,0.014,0.030,0.016,0.015,0.018,0.018];
y_sqr_std=[0.025,0.024,0.035,0.063,0.037,0.026,0.022,0.009];

%Tringle geometry data(Slide 10)
x_tri =     [0.22,  0.53,   0.82,   1.08,   1.39,   1.72,   2.07,   2.50];
y_tri =     [0.55,  0.53,   0.56,   0.56,   0.57,   0.62,   0.65,   0.57];
x_tri_std = [0.028, 0.012,  0.010,  0.021,  0.010,  0.011,  0.017,  0.024];
y_tri_std = [0.018, 0.012,  0.025,  0.046,  0.032,  0.026,  0.015,  0.013];

%All anchors on one side data(Slide 11)
x_one_side = [0.26, 0.55,   0.84,   1.10,   1.41,   1.68,   1.93,   2.29];
y_one_side = [0.30, 0.25,   0.24,   0.21,   0.44,   0.35,   0.36,   0.13];
x_one_side_std = [0.013,    0.011,  0.015,  0.017,  0.016,  0.011,  0.012,  0.020];
y_one_side_std = [0.059,    0.049,  0.073,  0.062,  0.041,  0.036,  0.040,  0.046];

%All anchors on one side with two anchors further away Slide 13
x_one_side_far = [0.23, 0.55,   0.79,   1.12,   1.39,   1.65,   1.93,   2.25];
y_one_side_far = [0.38, 0.40,   0.46,   0.49,   0.43,   0.37,   0.38,   0.28];
x_one_side_far_std = [0.021,  0.016,  0.023,  0.031,  0.014,  0.027,  0.022,  0.018];
y_one_side_far_std = [0.043,  0.041,  0.042,  0.046,  0.030,  0.042,  0.070,  0.075];


% Plotting with oval style standard deviation
title_1 = 'Square Anchor Geometry (Surrounding)';
pos_plot(X_TRUE, Y_TRUE, x_sqr, y_sqr, x_sqr_std, y_sqr_std,...
    x_anch_sqr, y_anch_sqr, BUFFER_POS, title_1);
title_2 = 'Triangle Anchor Geometry (Surrounding)';
pos_plot(X_TRUE, Y_TRUE, x_tri, y_tri, x_tri_std, y_tri_std,...
    x_anch_tri, y_anch_tri, BUFFER_POS, title_2);
title_3 = 'Single-Side Anchor Geometry, Smaller Anchor Spacing';
pos_plot(X_TRUE, Y_TRUE, x_one_side, y_one_side, x_one_side_std, y_one_side_std,...
    x_anch_one_side, y_anch_one_side, BUFFER_POS, title_3);
title_4 = 'Single-Side Anchor Geometry, Larger Anchor Spacing';
pos_plot(X_TRUE, Y_TRUE, x_one_side_far, y_one_side_far, x_one_side_far_std,y_one_side_far_std,...
    x_anch_one_side_far, y_anch_one_side_far, BUFFER_POS, title_4);
title_5='Two anchors blocked';
pos_plot(X_TRUE, Y_TRUE, x_anch_geo1, y_anch_geo1, x_anch_geo1_std,y_anch_geo1_std,...
    x_anch_exp4, y_anch_exp4, BUFFER_POS, title_5);
title_6='Two anchors blocked with one added';
pos_plot(X_TRUE, Y_TRUE, x_anch_geo2, y_anch_geo2, x_anch_geo2_std,y_anch_geo2_std,...
    x_anch_exp4_geo2, y_anch_exp4_geo2, BUFFER_POS, title_6);
title_7='Tag elevated';
pos_plot(X_TRUE, Y_TRUE, x_tag_elevated, y_tag_elevated, x_tag_elevated_std,y_tag_elevated_std,...
    x_anch_height, y_anch_height, BUFFER_POS, title_7);
title_8='Anchors elevated';
pos_plot(X_TRUE, Y_TRUE, x_anch_elevated, y_anch_elevated, x_anch_elevated_std,y_anch_elevated_std,...
    x_anch_height, y_anch_height, BUFFER_POS, title_8);


% Plotting with errorbar style
pos_errorbar(X_TRUE, Y_TRUE, x_sqr, y_sqr, x_sqr_std, y_sqr_std,...
    x_anch_sqr, y_anch_sqr, BUFFER_POS, 'Square Anchor Geometry (Surrounding)');
pos_errorbar(X_TRUE, Y_TRUE, x_tri, y_tri, x_tri_std, y_tri_std,...
    x_anch_tri, y_anch_tri, BUFFER_POS, 'Triangle Anchor Geometry (Surrounding)');
pos_errorbar(X_TRUE, Y_TRUE, x_one_side, y_one_side, x_one_side_std, y_one_side_std,...
    x_anch_one_side, y_anch_one_side, BUFFER_POS, 'Single-Side Anchor Geometry, Smaller Anchor Spacing');
pos_errorbar(X_TRUE, Y_TRUE, x_one_side_far, y_one_side_far, x_one_side_far_std,y_one_side_far_std,...
    x_anch_one_side_far, y_anch_one_side_far, BUFFER_POS, 'Single-Side Anchor Geometry, Larger Anchor Spacing');
pos_errorbar(X_TRUE, Y_TRUE, x_anch_geo1, y_anch_geo1, x_anch_geo1_std,y_anch_geo1_std,...
    x_anch_exp4, y_anch_exp4, BUFFER_POS, 'Two anchors blocked');
pos_errorbar(X_TRUE, Y_TRUE, x_tag_elevated, y_tag_elevated, x_tag_elevated_std,y_tag_elevated_std,...
    x_anch_height, y_anch_height, BUFFER_POS, 'Tag elevated');
pos_errorbar(X_TRUE, Y_TRUE, x_anch_elevated, y_anch_elevated, x_anch_elevated_std,y_anch_elevated_std,...
    x_anch_height, y_anch_height, BUFFER_POS, 'Anchors elevated');




function pos_plot(x_true, y_true, x_measure, y_measure, x_std, y_std, ...
    x_anch, y_anch, buffer_pos, title_name)
    % function call to plot according to different data
    % NO NEED TO COMMENT/UNCOMMENT
    % Display plot while done
    figure();
    set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
    hold on;
    % Plot the dummy handles for legend
    std_1 = plot(nan, nan, 'bo', 'MarkerFaceColor','b');
    buff = plot(nan, nan, 'LineStyle','--', 'Color','m','LineWidth',0.1);

    % Plot the std. deviation for all data points of geo1
    for i = 1:1:length(x_true)
        theta = 0 : 0.01 : 2*pi;
        xcenter = x_measure(i);
        ycenter = y_measure(i);
        xradius = x_std(i);
        yradius = y_std(i);
        x_s = xradius * cos(theta) + xcenter;
        y_s = yradius * sin(theta) + ycenter;
        h = fill(x_s,y_s,'b','facealpha',0.3);
        hold on
    end

    % Plot the connection from truth to measurements
    for i = 1:1:length(x_true)
        quiver(x_true(i), y_true(i), x_measure(i)-x_true(i), y_measure(i)-y_true(i),'color','k','LineStyle',':','LineWidth',0.3);
        hold on
    end

    % Plot the anchor positions
    anch = plot(x_anch, y_anch, 'b^');
    % Plot the buffer (+-10cm) for decawave
    rectangle('Position', buffer_pos, 'LineStyle',':', 'EdgeColor','m', 'Curvature', 1,'LineWidth',0.3);
    % Plot the true positions of tags
    plot_true_pos = plot(x_true, y_true, 'r.-','LineWidth',1);
    % Plot the measured positions of tags
    plot_measured = plot(x_measure, y_measure,'b-','LineWidth',2);
    axis([-0.5 3 -0.5 1.5]);
    daspect([1 1 1]);
    grid on;
    l = legend([plot_true_pos,plot_measured,std_1,anch,buff],...
        'True Position','Measured Position','Standard Deviation (Oval)',...
        'Anchor', 'Accuracy Buffer (±0.1m)');
    set(l, 'Location', 'northeast');
    title(title_name);
    xlabel('X coordinate (m)');
    ylabel('Y coordinate (m)');
    hold off;

end

function pos_errorbar(x_true, y_true, x_measure, y_measure, x_std, y_std, ...
    x_anch, y_anch, buffer_pos, title_name)
    % function call to plot according to different data, using errorbar
    % NO NEED TO COMMENT/UNCOMMENT
    % Display plot while done
    figure();
    set(gcf,'unit','normalized','position',[0.2, 0.2, 0.5, 0.5]);
    e1 = errorbar(x_measure, y_measure, y_std, y_std, x_std, x_std,...
        'Marker','o','LineStyle','-','LineWidth',2);
    hold on;
    % Plot the anchor positions
    anch = plot(x_anch, y_anch, 'b^');
    % Plot the dummy handles for legend
    buff = plot(nan, nan, 'LineStyle','--', 'Color','m','LineWidth',0.3);
    % replot in a zoomed-in manner
    rectangle('Position', buffer_pos, 'LineStyle',':', 'EdgeColor','m', 'Curvature', 1,'LineWidth',0.3);
    true_pos = plot(x_true, y_true, 'r.-','LineWidth',1);
    % Plot the connection from truth to measurements
    for i = 1:1:length(x_true)
        quiver(x_true(i), y_true(i), x_measure(i)-x_true(i), y_measure(i)-y_true(i),'color','k','LineStyle',':','LineWidth',0.3);
        hold on
    end
    daspect([1 1 1]);
    grid on;
    l = legend([true_pos,e1,buff,anch],'True Position','Measured Position','Accuracy Buffer (±0.1m)','Anchor');
    set(l, 'Location', 'northeast');
    axis([-0.5 3 -0.5 1.5]);
    title(title_name);
    xlabel('X coordinate (m)');
    ylabel('Y coordinate (m)');
end