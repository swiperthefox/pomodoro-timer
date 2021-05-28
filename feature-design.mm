<map version="freeplane 1.8.0">
<!--To view this file, download free mind mapping software Freeplane from http://freeplane.sourceforge.net -->
<node TEXT="New Functionality" FOLDED="false" ID="ID_732971614" CREATED="1620994978188" MODIFIED="1622170372598" STYLE="oval">
<font NAME="SansSerif" SIZE="16"/>
<hook NAME="AutomaticEdgeColor" COUNTER="0" RULE="ON_BRANCH_CREATION"/>
<hook NAME="MapStyle">
    <properties EDGECOLORCONFIGURATION="#808080ff,#ff0000ff,#0000ffff,#00ff00ff,#ff00ffff,#00ffffff,#7c0000ff,#00007cff,#007c00ff,#7c007cff,#007c7cff,#7c7c00ff" FIT_TO_VIEWPORT="false" SHOW_NOTE_ICONS="true" fit_to_viewport="false"/>

<map_styles>
<stylenode LOCALIZED_TEXT="styles.root_node" STYLE="oval" UNIFORM_SHAPE="true" VGAP_QUANTITY="24.0 pt">
<font SIZE="24"/>
<stylenode LOCALIZED_TEXT="styles.predefined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="default" ICON_SIZE="12.0 pt" COLOR="#000000" STYLE="fork"/>
<stylenode LOCALIZED_TEXT="defaultstyle.details"/>
<stylenode LOCALIZED_TEXT="defaultstyle.attributes"/>
<stylenode LOCALIZED_TEXT="defaultstyle.note" COLOR="#000000" BACKGROUND_COLOR="#ffffff" TEXT_ALIGN="LEFT"/>
<stylenode LOCALIZED_TEXT="defaultstyle.floating">
<cloud COLOR="#f0f0f0" SHAPE="ARC"/>
</stylenode>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.user-defined" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="styles.topic" COLOR="#18898b" STYLE="fork"/>
<stylenode LOCALIZED_TEXT="styles.subtopic" COLOR="#cc3300" STYLE="fork"/>
<stylenode LOCALIZED_TEXT="styles.subsubtopic" COLOR="#669900"/>
<stylenode LOCALIZED_TEXT="styles.important"/>
</stylenode>
<stylenode LOCALIZED_TEXT="styles.AutomaticLayout" POSITION="right" STYLE="bubble">
<stylenode LOCALIZED_TEXT="AutomaticLayout.level.root" COLOR="#000000" STYLE="oval" SHAPE_HORIZONTAL_MARGIN="10.0 pt" SHAPE_VERTICAL_MARGIN="10.0 pt"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,1" COLOR="#0033ff"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,2" COLOR="#00b439"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,3" COLOR="#990000"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,4" COLOR="#111111"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,5"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,6"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,7"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,8"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,9"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,10"/>
<stylenode LOCALIZED_TEXT="AutomaticLayout.level,11"/>
</stylenode>
</stylenode>
</map_styles>
</hook>
<node TEXT="task hierarchy" POSITION="right" ID="ID_1842737557" CREATED="1620995022637" MODIFIED="1622170372598">
<edge COLOR="#ff0000"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="create child task" ID="ID_1459462121" CREATED="1620995100277" MODIFIED="1622170372593">
<icon BUILTIN="full-1"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="represent of child task" ID="ID_842120474" CREATED="1620995617874" MODIFIED="1622170372598">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="a task can have a &quot;parent&quot; field" ID="ID_248539002" CREATED="1620995632501" MODIFIED="1622170372599">
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="every task has a &quot;children&quot; field" ID="ID_291291989" CREATED="1620995656017" MODIFIED="1622170372599">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="populated when the tasks are loaded" ID="ID_1116506589" CREATED="1621003023340" MODIFIED="1622170372599">
<icon BUILTIN="full-2"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="also can change when a subtask is created" ID="ID_342011260" CREATED="1621003051463" MODIFIED="1622170372605">
<icon BUILTIN="full-3"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
<node TEXT="render child task" ID="ID_1239780773" CREATED="1620995116697" MODIFIED="1622170372608">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="option 1: rerender all task" ID="ID_961637699" CREATED="1620995301298" MODIFIED="1622170372608">
<icon BUILTIN="full-5"/>
<icon BUILTIN="button_ok"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="option 2: add &quot;insert at&quot; event to TaskList" ID="ID_764503993" CREATED="1620995329151" MODIFIED="1622170372610">
<icon BUILTIN="button_cancel"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="option 3: add &quot;add child&quot; event" ID="ID_1563047737" CREATED="1620996061909" MODIFIED="1622170372613">
<icon BUILTIN="button_cancel"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="parent tasks are rendered with sparse grid_row" ID="ID_776800191" CREATED="1620996168642" MODIFIED="1622170372613">
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="every task keeps track of the row it is rendered in" ID="ID_1092025445" CREATED="1621004663618" MODIFIED="1622170372617">
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="child task can fit in it" ID="ID_1614195068" CREATED="1620996317104" MODIFIED="1622170372620">
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
<node TEXT="logic of &quot;done&quot;" FOLDED="true" ID="ID_637952839" CREATED="1620995123041" MODIFIED="1622170372620">
<icon BUILTIN="full-4"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="&quot;done&quot; should be disabled if some children are not &quot;done&quot;" ID="ID_90467439" CREATED="1620995912996" MODIFIED="1622170372620">
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="&quot;done&quot; is enabled when all its children are &quot;done&quot;" ID="ID_1343693035" CREATED="1620995987485" MODIFIED="1622170372625">
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
<node TEXT="repeated task" POSITION="right" ID="ID_1358529341" CREATED="1620995052194" MODIFIED="1622170372627">
<edge COLOR="#0000ff"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="manage repeated task" ID="ID_671740626" CREATED="1621001414392" MODIFIED="1622170372628">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="create repeated task" ID="ID_1106007495" CREATED="1621000796441" MODIFIED="1622170372628">
<icon BUILTIN="full-1"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="table &quot;repeated-task&quot;" ID="ID_634221571" CREATED="1621000872136" MODIFIED="1622170372629">
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node TEXT="mark a task done" ID="ID_1762519617" CREATED="1621001430230" MODIFIED="1622170372630">
<font NAME="SansSerif" SIZE="16"/>
</node>
<node TEXT="GUI for repeated task managment" ID="ID_1927542788" CREATED="1621005950029" MODIFIED="1622170372631">
<icon BUILTIN="full-2"/>
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
<node TEXT="schedule task" ID="ID_818378497" CREATED="1621000919653" MODIFIED="1622170372633">
<icon BUILTIN="full-3"/>
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="When" ID="ID_356062373" CREATED="1621008555298" MODIFIED="1622170372633">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="do schedule at the start of every day" ID="ID_374049058" CREATED="1621000928793" MODIFIED="1622170372633">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="load unfinished from repeated task" ID="ID_154200377" CREATED="1621001151045" MODIFIED="1622170372635">
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
<node TEXT="How" ID="ID_785238637" CREATED="1621008537178" MODIFIED="1622170372636">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="for each task" FOLDED="true" ID="ID_985779117" CREATED="1621001335626" MODIFIED="1622170372637">
<font NAME="SansSerif" SIZE="16"/>
<node TEXT="schedule for today" ID="ID_1437182385" CREATED="1621001347102" MODIFIED="1621001363763"/>
<node TEXT="if there is no next occurance, remove it" ID="ID_1154490608" CREATED="1621001366030" MODIFIED="1621001397701"/>
</node>
<node TEXT="avoid double schedule" ID="ID_1717655012" CREATED="1621001884626" MODIFIED="1622170372637">
<font NAME="SansSerif" SIZE="16"/>
</node>
</node>
</node>
</node>
</node>
</map>
